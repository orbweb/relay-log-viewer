from parse.models import RelaySession, RelayEntry
from django.shortcuts import get_object_or_404, render


def show_sessions(request):
    active = True if request.GET.get('active') else False
    sessions = RelaySession.objects.filter(active=active).order_by('start_time')
    return render(request, 'sessions/show.html', {
        'sessions': sessions
    })
