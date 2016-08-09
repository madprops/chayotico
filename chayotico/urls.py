import os
from django.conf.urls import patterns, include, url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': BASE_DIR + '/media/'}),
    (r'^$', 'server.views.main'),
    (r'^login/$', 'server.views.login'),
    (r'^register/$', 'server.views.register'),
    (r'^logout/$', 'server.views.logout'),
    (r'^delete_thread/(?P<id>\w+)/$', 'server.views.delete_thread'),
    (r'^delete_post/$', 'server.views.delete_post'),
    (r'^ban/$', 'server.views.ban'),
    (r'^raise_thread/(?P<id>\w+)/$', 'server.views.raise_thread'),
    (r'^error/(?P<code>\w+)/$', 'server.views.error'),
    (r'^notifications/$', 'server.views.notifications'),
    (r'^check_notifs/$', 'server.views.check_notifs'),
    (r'^(?P<board>\w+)/$', 'server.views.board'),
    (r'^(?P<board>\w+)/(?P<id>\w+)/$', 'server.views.thread'),
)
