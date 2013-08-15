from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json


HOURLY_LOG_CONFIG_PATH = settings.HOURLY_LOG_CONFIG_PATH
LOG_CONFIG_PATH = settings.LOG_CONFIG_PATH


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(LOG_CONFIG_PATH, 'r') as jsonf:
            json_data = json.loads(jsonf.read())
            files = json_data['files']
            for file_json in files:
                if 'latest' in file_json:
                    file_json.pop('latest')
        with open(LOG_CONFIG_PATH, 'w') as jsonf:
            jsonf.write(json.dumps(json_data, sort_keys=True, indent=2,
                        separators=(',', ': ')))

        with open(HOURLY_LOG_CONFIG_PATH, 'r') as jsonf:
            json_data = json.loads(jsonf.read())
            if 'latest' in json_data:
                json_data.pop('latest')

        with open(HOURLY_LOG_CONFIG_PATH, 'w') as jsonf:
            jsonf.write(json.dumps(json_data, sort_keys=True, indent=2,
                        separators=(',', ': ')))
