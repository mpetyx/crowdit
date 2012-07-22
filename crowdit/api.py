__author__ = 'mpetyx'

from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login, logout
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization, DjangoAuthorization#, MultiAuthentication
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication#OAuthAuthentication#, MultiAuthentication
from authentication import TwoLeggedOAuthAuthentication
from tastypie.cache import SimpleCache
from tastypie.validation import Validation
from tastypie.utils import trailing_slash
from django.db import models
from tastypie.models import create_api_key
from models import OAuthConsumer
from CamelCaseJSONSerializer import CamelCaseJSONSerializer
from models import Person, User

"""
    the closed api we are going to expose for the mobile devices
"""


# a class for handling custom authentication as already described
class MyAuthentication(BasicAuthentication):

    def is_authenticated(self, request, **kwargs):

        from django.contrib.auth.models import User

        username = request.GET.get('username') or request.POST.get('username')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')

        if not username or not api_key:
            return self._unauthorized()

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        request.user = user
        return self.get_key(user, api_key)


#        http://stackoverflow.com/questions/10778916/create-a-new-user-using-tastypie-results-in-401
#        curl -v -X POST -d '{"username" : "username", "password" : "123456"}' -H "Authorization: ApiKey superusername:apikey" -H "Content-Type: application/json" http://127.0.0.1:8000/api/v1/newuser/
class UserSignUpResource(ModelResource):

    """
    example on how it works
    curl -v -X POST -d '{"username" : "foo", "password" : "bar"}' -H "Authorization:ApiKey" -H "Content-Type: application/json" http://127.0.0.1:8000/api/crowdit/newuser/\?username\=dev\&api_key\=5d56fb13fd56ed00f96b080663dee25d80811143
    """

    class Meta:
        object_class = User
        queryset = User.objects.all()
        allowed_methods = ['post']
        include_resource_uri = False
        resource_name = 'newuser'
        excludes = ['is_active', 'is_staff', 'is_superuser']
        serializer = CamelCaseJSONSerializer(formats=['json'])
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        models.signals.post_save.connect(create_api_key, sender=User)

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(UserSignUpResource, self).obj_create(bundle, request, **kwargs)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('The username already exists')
        return bundle

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(id=request.user.id, is_superuser=True)

class UserResource(ModelResource):

        class Meta:

            queryset = User.objects.all()
            list_allowed_methods = ['get', 'post']

            #        fields = ['username', 'first_name', 'last_name', 'last_login']
            #        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
            #        allowed_methods = ['get']

            authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
            authorization = DjangoAuthorization()

            excludes = ['id']
            include_resource_uri = False

        def override_urls(self):

            return [
                url(r"^(?P<resource_name>%s)/signin%s$" %
                    (self._meta.resource_name, trailing_slash()),
                    self.wrap_view('signin'), name="api_signin"),
                url(r"^(?P<resource_name>%s)/logout%s$" %
                    (self._meta.resource_name, trailing_slash()),
                    self.wrap_view('logout'), name="api_logout"),
            ]


        def signin(self, request, **kwargs):
            self.method_check(request, allowed=['post'])

            # Per https://docs.djangoproject.com/en/1.3/topics/auth/#django.contrib.auth.login...
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    consumer = OAuthConsumer()
                    consumer.key = 'foo'
                    consumer.name = 'foo'
                    consumer.secret = 'foo'
                    consumer.active = True
                    consumer.save()
                    return self.create_response(request, {'success': True, 'key': consumer.key})
                else:
                    # Return a 'disabled account' error message
                    return self.create_response(request, {'success': False})
            else:
                # Return an 'invalid login' error message.
                return self.create_response(request, {'success': False})


        def logout(self, request, **kwargs):
            self.method_check(request, allowed=['post'])

            logout(request)
