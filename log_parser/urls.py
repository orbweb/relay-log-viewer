from django.conf.urls import patterns, include, url
from django.contrib import admin
import parse.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^view/', include('parse.urls')),
    url(r'^$', parse.views.charts),

    url(r'^admin/', include(admin.site.urls)),
)
