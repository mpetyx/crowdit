from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login, logout
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization, DjangoAuthorization#, MultiAuthentication
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication#OAuthAuthentication#, MultiAuthentication
from authentication import *
from tastypie.cache import SimpleCache
from tastypie.validation import Validation
from tastypie.utils import trailing_slash
from django.db import models
from django.conf import settings
from tastypie.models import create_api_key
from models import OAuthConsumer
from CamelCaseJSONSerializer import CamelCaseJSONSerializer
from models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import time
import os

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
# curl -v -X POST -d 'username=yalll&password=yall' -H "Authorization:ApiKey" -H "Content-Type: application/json" http://127.0.0.1:8000/api/crowdit/newuser/\?username\=dev\&api_key\=5d56fb13fd56ed00f96b080663dee25d80811143

    class Meta:
        object_class = Person
        queryset = Person.objects.all()
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

            authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
            authorization = DjangoAuthorization()

            excludes = ['id']
            include_resource_uri = False

        def override_urls(self):

            return [
                url(r"^(?P<resource_name>%s)/signin%s$" %
                    (self._meta.resource_name, trailing_slash()),
                    self.wrap_view('signin'), name="api_signin"),
                url(r"^(?P<resource_name>%s)/prof_picture_upload%s$" %
                    (self._meta.resource_name, trailing_slash()),
                    self.wrap_view('prof_picture_upload'), name="api_prof_picture_upload"),
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
                    consumer, created = OAuthConsumer.objects.get_or_create(key=user.username, name=user.username,
                        active=True)
                    consumer.secret = user.username + str(time.time())
                    consumer.save()
                    return self.create_response(request, {'success': True, 'name': user.username, 'key': consumer.key, 'secret': consumer.secret})
                else:
                    # Return a 'disabled account' error message
                    return self.create_response(request, {'success': False, 'message': 'The user is disabled'})
            else:
                # Return an 'invalid login' error message.
                return self.create_response(request, {'success': False, 'message': 'Invalid User. Please make sure you inserted the right username-password'})


        def prof_picture_upload(self, request, **kwargs):
            consumer_key = get_oauth_consumer_key_from_header(request.META.get('HTTP_AUTHORIZATION'))
            try:
                consumer = OAuthConsumer.objects.get(key=consumer_key)
            except OAuthConsumer.DoesNotExist:
                consumer = None
            if not consumer:
                return self._unauthorized()
            else:
                user = Person.objects.get(username=consumer.key)
            if not user:
                return self._unauthorized()
            else:
                request.user = user
            self.is_authorized(request)
            uploaded_file = request.FILES['file']
            user.photo.save(str(user.id) + '.jpg', ContentFile(uploaded_file.read()))
            user.save
            return self.create_response(request, {'success': True, 'message': 'WOW!!'})


        def logout(self, request, **kwargs):
            self.method_check(request, allowed=['post'])

            logout(request)


class EventResource(ModelResource):

    class Meta:

        object_class = Event
        queryset = Event.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
#        excludes = ['is_active', 'is_staff', 'is_superuser']
        resource_name = 'event'

#        authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
#        authorization = DjangoAuthorization()

        excludes = ['id']
        include_resource_uri = False

class AwardResource(ModelResource):

    class Meta:

        object_class = Award
        queryset = Award.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        resource_name = 'award'
#        excludes = ['is_active', 'is_staff', 'is_superuser']
#        authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
#        authorization = DjangoAuthorization()


class FriendshipInvitationResourse(ModelResource):

    class Meta:

        queryset = FriendshipInvitation.objects.all()
        allowed_methods = ['post']
        authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
        authorization = DjangoAuthorization()
        excludes = ['id']
        resource_name = 'invite'
        include_resource_uri = False

    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/send%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('send'), name="api_send"),
            url(r"^(?P<resource_name>%s)/validate%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('validate'), name="api_validate"),
            ]


    def send(self, request, **kwargs):
#        self.is_authenticated(request)
#        the code below will work perfect when the line above will be uncommented
        consumer_secret = get_oauth_consumer_key_from_header(request.META.get('HTTP_AUTHORIZATION'))
        try:
            consumer = OAuthConsumer.objects.get(secret=consumer_secret)
        except OAuthConsumer.DoesNotExist:
            consumer = None
        if not consumer:
            return self._unauthorized()
        else:
            user = Person.objects.get(username=consumer.key)
        if not user:
            return self._unauthorized()
        else:
            request.user = user
        self.is_authorized(request)
        to_user_id = request.POST.get('username_to', '');
        to_user = Person.objects.get(id=to_user_id)
        to_user_username = to_user.username
        from_user_id = user.id
        from_user = user
        if Friendship.objects.are_friends(to_user_id, from_user_id):
            return self.create_response(request, {'success': False, 'message': 'It seems that you are already friends with ' + to_user_username})
        else:
            invitations = FriendshipInvitation.objects.invitations(from_user=from_user_id,to_user=to_user_id)
            if (not invitations):
                invitation = FriendshipInvitation.objects.get_or_create(from_user=from_user, to_user=to_user,
                    message='Hello! Do you wanna join me on crowdit??', status=1)
#                invitation.save()
                return self.create_response(request, {'success': True, 'message': 'Hey ' +  user.username + '!' +
                      'You successfully sent invitation to ' + to_user_username})
            else:
                return self.create_response(request, {'success': False, 'message': 'It seems that there is already a pending invitation for ' + to_user_username})

    def validate(self, request, **kwargs):
        invitation_id = request.GET.get('invitationID', '');
        return self.create_response(request, {'success': True, 'message': 'Successfully Validated User From Invitation To User To' + invitation_id})

