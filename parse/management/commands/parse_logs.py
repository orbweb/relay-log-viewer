from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import re
from glob import glob
from datetime import datetime
import os
import parse
from pytz import timezone

LOGS_PATH = settings.LOGS_PATH
CONFIG_PATH = settings.LOG_CONFIG_PATH

def line_to_cols(line, convert_from_unix, tzinfo):
    field_sep_re = re.compile(']|\s+')
    cols = re.split(field_sep_re, line.lstrip('[').rstrip())
    res = [' '.join(cols[0:2])] + cols[2:]
    for i in convert_from_unix:
        res[i] = datetime.fromtimestamp(float(res[i]), timezone('UTC'))
    for i, tz in tzinfo.iteritems():
        res[i] = tz.localize(datetime.strptime(res[i], '%Y-%m-%d %H:%M:%S'))
    return res

def insert(data, column_names, class_name):
    klass = getattr(parse.models, class_name)
    objs = [klass(**dict(zip(column_names, datum))) for datum in data]
    klass.objects.bulk_create(objs)

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(CONFIG_PATH, 'r') as jsonf:
            json_data = json.loads(jsonf.read())
            files = json_data['files']
            for file_json in files:
                if 'latest' in file_json and file_json['latest']:
                    log_names = sorted([
                        name for name in glob(file_json['pattern'])
                        if name > file_json['latest']])
                else:
                    log_names = sorted(glob(os.path.join(
                        LOGS_PATH, file_json['pattern'])))
                    file_json['latest'] = log_names[-1]

                convert_from_unix = [file_json['columns'].index(c)
                                     for c in file_json['convert_from_unix']]
                tzinfo = dict((file_json['columns'].index(col), timezone(tz))
                    for col, tz in file_json['tzinfo'].iteritems())

                for log_name in log_names:
                    print 'Opening %s...' % log_name
                    with open(log_name) as log:
                        col_data = (line_to_cols(line, convert_from_unix, tzinfo)
                                    for line in log)
                        insert(
                            col_data, file_json['columns'],
                            file_json['model_name'])

        with open(CONFIG_PATH, 'w') as jsonf:
            jsonf.write(json.dumps(json_data, sort_keys=True, indent=2,
                                   separators=(',', ': ')))
