from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import re
from glob import glob
from datetime import datetime
import os
from parse.models import RelaySession, RelayEntry
from pytz import timezone
from bisect import bisect_left

LOGS_PATH = settings.LOGS_PATH

# (name regex, split regex, create new object)
line_types = [
    # regex groups: timestamp and uid
    ('Relay Request', 'UID=(?P<uid>.*?),', True),
    # regex groups: timestamp
    ('MSG_CONNECT_SUCCESS.*?Mode:1', '^\[(?P<start_time>.*?)\].*?D\:\((?P<uid>.*?),', False),
]


obj_cache = {}


def process(line, split_re, create_new):
    match = re.search(split_re, line)
    if match:
        cols_dict = match.groupdict()
    else:
        raise Exception(
            'Something is wrong with your split regex: %s\nline:%s' %
            (split_re, line))

    if create_new:
        relay_session = RelaySession(**cols_dict)
        obj_cache[cols_dict['uid']] = relay_session
    else:
        # attempt to get obj from cache, or retrieve from db if not available
        # set all the new attributes and return the obj
        try:
            relay_session = obj_cache.pop(cols_dict['uid'])
        except KeyError:
            try:
                relay_session = RelaySession.objects.get(
                    active=True, uid=cols_dict['uid'])
            except RelaySession.DoesNotExist:
                return

        for field, val in cols_dict.iteritems():
            if field is not 'uid':
                if re.match('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', val):
                    date = timezone('US/Eastern').localize(
                        datetime.strptime(val, '%Y-%m-%d %H:%M:%S'))
                    setattr(relay_session, field, date)
                else:
                    setattr(relay_session, field, val)

        return relay_session


def files_lines(files):
    for fname in files:
        with open(fname, 'r') as f:
            for line in f:
                yield line


# http://docs.python.org/2/library/bisect.html#searching-sorted-lists
def obj_index(obj, objs):
    i = bisect_left(objs, obj)
    if i != len(objs) and objs[i] == obj:
        return i
    #print '%s closest: %s' % (map(str, obj), map(str, objs[i]))
    return None

def log_relay_objs(files):
    started_session_objs = []
    for line in files_lines(files):
        for name_re, split_re, create_new in line_types:
            if re.search(name_re, line):
                obj = process(line, split_re, create_new)
                if obj:
                    started_session_objs.append(obj)

    # add end_times
    # figure out how to make this better
    uids, dates = zip(*[(obj.uid, obj.start_time)
        for obj in started_session_objs if obj.start_time is not None])
    relay_entries = list(RelayEntry.objects.filter(uid__in=uids).order_by(
        'uid', 'start_time'))
    #print 'len(started_session_objs) = %d' % len(started_session_objs)
    #print 'len(relay_entries) = %d' % len(relay_entries)
    relay_entry_tuples = [(obj.uid, obj.start_time) for obj in relay_entries]
    found_count = 0
    none_count = 0
    for session in started_session_objs:
        index = obj_index((session.uid, session.start_time), relay_entry_tuples)
        if index:
            session.end_time = relay_entries[index].end_time
            session.active = False

    return started_session_objs


class Command(BaseCommand):
    def handle(self, *args, **options):
        hourly_name_re = re.compile('\d+.txt')
        hourly_logs = (name for name in glob(os.path.join(LOGS_PATH, '*.txt'))
            if hourly_name_re.search(name))

        '''
        counts = {}
        log_counts = 0
        for log_name in hourly_logs:
            #print 'Processing %s...' % log_name
            log_counts += 1
            with open(log_name, 'r') as log:
                # order of lines matters, so we cannot use a 'findall'
                # like method
                objs = list(log_relay_objs(log))
                RelaySession.objects.bulk_create(objs)
        '''
        sessions = log_relay_objs(hourly_logs)
        print sessions
        print len(sessions)
        RelaySession.objects.bulk_create(sessions)

        #print 'processed: %d' % log_counts
