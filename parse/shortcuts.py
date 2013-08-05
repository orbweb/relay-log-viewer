import json
from django.http import HttpResponse
from django.core import serializers
from datetime import datetime

def json_response(a_dict, dump=True):
    return HttpResponse(json.dumps(a_dict), mimetype='application/json')


def dict_dates_to_str(a_list):
    for obj in a_list:
        for k, v in obj.iteritems():
            if isinstance(v, datetime):
                obj[k] = str(v)

    return list(a_list)
