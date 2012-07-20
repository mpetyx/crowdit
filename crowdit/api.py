__author__ = 'mpetyx'

from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization, DjangoAuthorization#, ApiKeyAuthentication
from tastypie.authentication import BasicAuthentication
from tastypie.cache import SimpleCache
from tastypie.validation import Validation
from tastypie.utils import trailing_slash

import CamelCaseJSONSerializer
from models import User

