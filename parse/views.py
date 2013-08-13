from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.conf import settings
from parse.models import RelaySession, RelayEntry
from parse.shortcuts import json_response, dict_dates_to_str
from django.core import serializers
import simplejson
import numpy
from collections import Counter


def show_sessions(request):
    active = True if request.GET.get('active') else False
    sessions = RelaySession.objects.filter(active=active).order_by(
        'start_time')
    return render(request, 'sessions/show.html', {
        'sessions': sessions
    })


def get_sessions(request, active):
    page = request.GET.get('page')
    if active == 'all':
        sessions = RelaySession.objects.all().order_by('-start_time').values()
    else:
        active = True if active == 'true' else False
        sessions = RelaySession.objects.filter(
            active=active).order_by('-start_time').values()

    if page:
        pag = Paginator(sessions, 500)
        try:
            sessions = pag.page(page)
        except EmptyPage:
            sessions = {}

    #return json_response(serializers.serialize('json', sessions, fields=('uid', 'start_time', 'end_time', 'active')), dump=False)
    return json_response(dict_dates_to_str(sessions))


def charts(request):
    relay_sessions = RelaySession.objects.filter(active=False).select_related(
        'relay_entry__data')
    data_transfer_list = [rs.relay_entry.data for rs in relay_sessions]
    stats = [
        {
            'name': 'Average data transfered per session',
            'val': int(
                numpy.mean(data_transfer_list))/1000,
            'units': 'megabytes',
        },
        {
            'name': 'Median data transfered per session',
            'val': int(
                numpy.median(data_transfer_list))/1000,
            'units': 'megabytes',
        },
        {
            'name': 'Deviation of data transfered per session',
            'val': int(
                numpy.std(data_transfer_list))/1000,
            'units': 'megabytes',
        },
    ]
    return render(request, 'sessions/charts.html', {
        'stats': stats,
    })


def charts_json(request, chart_type):
    if chart_type == 'uid_data':
        uid_data_counts = {}
        relay_sessions = RelaySession.objects.filter(active=False).select_related(
            'relay_entry__data')
        for session in relay_sessions:
            if session.uid not in uid_data_counts:
                uid_data_counts[session.uid] = 0
            uid_data_counts[session.uid] += session.relay_entry.data
        uid_data_counts = [{'category': k, 'data': v}
                           for k, v in uid_data_counts.iteritems()]
        return json_response(uid_data_counts)

    elif chart_type == 'end_reasons':
        end_reason_counts = Counter()
        relay_sessions = RelaySession.objects.filter(active=False).values(
            'relay_entry__end_reason')
        for reason in (rs['relay_entry__end_reason'] for rs in relay_sessions):
            end_reason_counts[reason] += 1

        counts = [{'category': settings.END_REASONS[k], 'data': v}
                  for k, v in end_reason_counts.iteritems()]
        return json_response(counts)
