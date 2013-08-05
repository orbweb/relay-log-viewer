from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from parse.models import RelaySession, RelayEntry
from parse.shortcuts import json_response, dict_dates_to_str
from django.core import serializers
import simplejson


def show_sessions(request):
    active = True if request.GET.get('active') else False
    sessions = RelaySession.objects.filter(active=active).order_by('start_time')
    return render(request, 'sessions/show.html', {
        'sessions': sessions
    })

def get_sessions(request):
    page = request.GET.get('page')
    sessions = RelaySession.objects.all().order_by('start_time').values()
    if page:
        pag = Paginator(sessions, 500)
        try:
            sessions = pag.page(page)
        except EmptyPage:
            sessions = {}

    #return json_response(serializers.serialize('json', sessions, fields=('uid', 'start_time', 'end_time', 'active')), dump=False)
    return json_response(dict_dates_to_str(sessions))
