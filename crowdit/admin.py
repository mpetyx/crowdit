__author__ = 'mpetyx'

from tastypie.models import ApiAccess, ApiKey
from models import OAuthConsumer
from django.contrib import admin

admin.site.register(ApiKey)
admin.site.register(ApiAccess)
admin.site.register(OAuthConsumer)
