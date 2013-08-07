from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.transaction import commit_on_success
import re
from glob import glob
from datetime import datetime
import os
from parse.models import RelaySession, RelayEntry
from pytz import timezone
from bisect import bisect_left
import json

LOGS_PATH = settings.LOGS_PATH
HOURLY_CONFIG = settings.HOURLY_LOG_CONFIG_PATH

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


@commit_on_success
def update_objs(objs):
    for obj in objs:
        obj.save()


# http://docs.python.org/2/library/bisect.html#searching-sorted-lists
def obj_index(obj, objs):
    i = bisect_left(objs, obj)
    if i != len(objs) and objs[i] == obj:
        return i
    return None

def match_sessions_with_entries(sessions):
    if len(sessions) > 0:
        uids, dates = zip(*[(session.uid, session.start_time)
            for session in sessions if session.start_time is not None])
        relay_entries = list(RelayEntry.objects.filter(uid__in=uids).order_by(
            'uid', 'start_time'))

        relay_entry_tuples = [(obj.uid, obj.start_time) for obj in relay_entries]
        for session in sessions:
            index = obj_index((session.uid, session.start_time), relay_entry_tuples)
            if index:
                session.end_time = relay_entries[index].end_time
                session.active = False

    return sessions

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
    relay_entry_tuples = [(obj.uid, obj.start_time) for obj in relay_entries]
    for session in started_session_objs:
        index = obj_index((session.uid, session.start_time), relay_entry_tuples)
        if index:
            session.end_time = relay_entries[index].end_time
            session.active = False

    match_sessions_with_entries(started_session_objs)

    return started_session_objs


class Command(BaseCommand):
    def handle(self, *args, **options):
        # update old sessions that don't have an end time
        updated_sessions = match_sessions_with_entries(
            RelaySession.objects.filter(end_time=None))
        update_objs(updated_sessions)

        hourly_name_re = re.compile('/\d+.txt')
        with open(HOURLY_CONFIG, 'r') as jsonf:
            json_data = json.loads(jsonf.read())
            if 'latest' in json_data and json_data['latest']:
                hourly_logs = sorted([name
                    for name in glob(os.path.join(LOGS_PATH, '*.txt'))
                    if name > json_data['latest'] and \
                    hourly_name_re.search(name)])
                if len(hourly_logs) > 0:
                    json_data['latest'] = hourly_logs[-1]
            else:
                hourly_logs = sorted([name
                    for name in glob(os.path.join(LOGS_PATH, '*.txt'))
                    if hourly_name_re.search(name)])
                json_data['latest'] = hourly_logs[-1]

            if len(hourly_logs) > 0:
                sessions = log_relay_objs(hourly_logs)
                RelaySession.objects.bulk_create(sessions)

        with open(HOURLY_CONFIG, 'w') as jsonf:
            jsonf.write(json.dumps(json_data, sort_keys=True, indent=2,
                                   separators=(',', ': ')))
