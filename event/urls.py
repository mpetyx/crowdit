from django.conf.urls.defaults import *
urlpatterns = patterns('',
        (r'(?P<event_id>\d+)/$', 'event.views.image'),
    )
