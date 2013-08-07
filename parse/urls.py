from django.conf.urls import patterns, url
urlpatterns = patterns('parse.views',
    url(r'^sessions/$', 'show_sessions', name='show-sessions'),
    url(r'^sessions/(?P<active>\w+)/.json$', 'get_sessions', name='get-sessions'),
    url(r'^charts/$', 'charts', name='charts'),
    url(r'^charts/(?P<chart_type>\w+).json$', 'charts_json', name='charts_json'),
)
