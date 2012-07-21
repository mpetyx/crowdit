#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from crowdit.api import  UserSignUpResource,UserResource
from tastypie.api import Api

from django.contrib import admin
admin.autodiscover()

crowdit_api = Api(api_name='crowdit')
crowdit_api.register(UserSignUpResource())
crowdit_api.register(UserResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'crowdit.views.home', name='home'),
    # url(r'^crowdit/', include('crowdit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^api/', include(crowdit_api.urls)),
    url(r'social', include('social_auth.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
