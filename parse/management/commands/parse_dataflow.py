from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from parse.models import DataflowMonth
from glob import glob
import re
import os
from itertools import izip

LOGS_PATH = settings.LOGS_PATH

TIME_RE = 'Dataflow(?P<year>\d{4})(?P<month>\d{2})'

COL_NAMES = (
    'packets_sent',
    'packets_recieved',
    'bytes_sent',
    'bytes_recieved',
    'relay_packets',
    'relay_bytes',
    'relay_connections',
    'p2p_connections'
)

def line_to_cols(line):
    return re.split('\s+', line.split(']')[1].rstrip())

def file_lines(f_name):
    with open(f_name, 'r') as f:
        for line in f:
            yield line

class Command(BaseCommand):
    def handle(self, *args, **options):
        for f_name in glob(os.path.join(LOGS_PATH, 'Dataflow*.txt')):
            # find the DataflowMonth record
            year_month = re.search(TIME_RE, f_name).groupdict()
            try:
                dataflow_month = DataflowMonth.objects.get(**year_month)
            except DataflowMonth.DoesNotExist:
                dataflow_month = DataflowMonth(**year_month)

            for line in file_lines(f_name):
                line_col_vals = line_to_cols(line)
                # add line values to DataflowMonth object
                for col_name, col_val in izip(COL_NAMES, line_col_vals):
                    # cannot use getattr's default because the models
                    # automatically fill in None for the field value if not
                    # specified upon instantiation
                    if getattr(dataflow_month, col_name):
                        setattr(
                            dataflow_month, col_name,
                            getattr(dataflow_month, col_name) + int(col_val))
                    else:
                        setattr(dataflow_month, col_name, int(col_val))

            dataflow_month.save()
