#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from crowdit.api import *
from tastypie.api import Api
from django.conf import settings
from django.contrib import admin
from django.views.static import *
from django.conf import settings

admin.autodiscover()

crowdit_api = Api(api_name='crowdit')
crowdit_api.register(UserSignUpResource())
crowdit_api.register(UserResource())
crowdit_api.register(EventResource())
crowdit_api.register(AwardResource())


urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^api/', include(crowdit_api.urls)),
    url(r'social', include('social_auth.urls')),

     url(r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.abspath('media')}),
    )