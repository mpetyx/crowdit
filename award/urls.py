from django.conf.urls.defaults import *
urlpatterns = patterns('',
        (r'(?P<award_id>\d+)/$', 'award.views.image'),
    )
