__author__ = 'mpetyx'

from tastypie.models import ApiAccess, ApiKey
from django.contrib import admin

admin.site.register(ApiKey)
admin.site.register(ApiAccess)