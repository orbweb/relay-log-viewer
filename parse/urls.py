from django.conf.urls import patterns, url
urlpatterns = patterns('parse.views',
    url(r'^sessions/$', 'show_sessions', name='show-sessions'),
    url(r'^sessions/.json$', 'get_sessions', name='get-sessions'),
)
