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
from django.utils import simplejson
from models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from django.http import HttpResponse, HttpResponseNotFound
from tastypie import http
import time
import datetime
import os

"""
    the closed api we are going to expose for the mobile devices
"""

# a class for handling custom authentication as already described
class MyAuthentication(BasicAuthentication):

    def is_authenticated(self, request, **kwargs):
        username = request.GET.get('username') or request.POST.get('username')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')

        if not username or not api_key:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

        try:
            user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

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

        queryset = Person.objects.all()
        list_allowed_methods = ['get', 'post']

        authentication = TwoLeggedOAuthAuthentication() #MultiAuthentication(BasicAuthentication, MyAuthentication())
        authorization = DjangoAuthorization()
        excludes = ['password', 'is_superuser']
        include_resource_uri = False

    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/signin%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('signin'), name="api_signin"),
            url(r"^(?P<resource_name>%s)/search%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('search'), name="api_search"),
            url(r"^(?P<resource_name>%s)/friends%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('friends'), name="api_friends"),
            url(r"^(?P<resource_name>%s)/prof_picture_upload%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('prof_picture_upload'), name="api_prof_picture_upload"),
            url(r"^(?P<resource_name>%s)/logout%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name="api_logout"),
        ]


    def search(self, request, **kwargs):
        self.is_authenticated(request)
        checkRequestAndGetRequester(self, request)
        username = request.GET['username'];
        if username:
            try:
                person = Person.objects.get(username=username)
            except OAuthConsumer.DoesNotExist:
                person = None
            if person:
                url = person.photo.url if person.photo else ''
                return self.create_response(request, {'success': True, 'userID': person.id, 'user': person.username, 'photo': url})
            else:
                return self.create_response(request, {'success': False, 'message': 'User not found'})
        else:
            return self.create_response(request, {'success': False, 'message': 'Please provide a username'})


    def friends(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request)
        friends = friend_set_for(person)
        if friends:
            jsonFriends = simplejson.dumps([{'username': friend.username, 'id': friend.id, 'photo': friend.photo.url if friend.photo else ''} for friend in friends])
            return self.create_response(request, {'success': True, 'friends': jsonFriends})
        else:
            return self.create_response(request, {'success': False, 'message': 'No friends found'})


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
                person = Person.objects.get(username=user.username)
                return self.create_response(request, {'success': True, 'profilePictureUrl': person.photo.url if person.photo else '', 'name': user.username, 'key': consumer.key, 'secret': consumer.secret})
            else:
                # Return a 'disabled account' error message
                return self.create_response(request, {'success': False, 'message': 'The user is disabled'})
        else:
            # Return an 'invalid login' error message.
            return self.create_response(request, {'success': False, 'message': 'Invalid User. Please make sure you inserted the right username-password'})


    def prof_picture_upload(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request)
        uploaded_file = request.FILES['file']
        person.photo.save(str(person.id) + '.jpg', ContentFile(uploaded_file.read()))
        person.save
        return self.create_response(request, {'success': True, 'profilePictureUrl': person.photo.url})


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


class FriendshipInvitationResource(ModelResource):

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
            url(r"^(?P<resource_name>%s)/accept%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('accept'), name="api_accept"),
            url(r"^(?P<resource_name>%s)/decline%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('decline'), name="api_decline"),
            url(r"^(?P<resource_name>%s)/pending%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('pending'), name="api_pending"),
            url(r"^(?P<resource_name>%s)/read%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('read'), name="api_read"),
            ]


    def read(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request)
#        person = Person.objects.get(username='Foo')
#        request.user = person
        invitation_ids = request.POST.get('invitationIDs', '')
        invitation = False
        invitations = False
        if invitation_ids.find(',') == -1:
            invitation = FriendshipInvitation.objects.get(id=invitation_ids)
        else:
            invitations = FriendshipInvitation.objects.filter(id__in=eval(invitation_ids))
        if (invitations):
            for invitation in invitations:
                if invitation.to_user == person:
                    invitation.date_read = datetime.datetime.now()
                    invitation.save()
                else:
                    return self.create_response(request, {'success': False, 'message': 'Come on stop trying to hack this app!'})
            return self.create_response(request, {'success': True})
        elif (invitation):
            if invitation.to_user == person:
                invitation.date_read = datetime.datetime.now()
                invitation.save()
                return self.create_response(request, {'success': True})
            else:
                return self.create_response(request, {'success': False, 'message': 'Come on stop trying to hack this app!'})
        else:
            return self.create_response(request, {'success': False, 'message': 'No invitations found!'})


    def send(self, request, **kwargs):
        self.is_authenticated(request)
        user = checkRequestAndGetRequester(self, request)
        #        the code below will work perfect when the line above will be uncommented and the two lines below will be commented
#        user = Person.objects.get(username='Johnecon')
#        request.user = user

        to_user_id = request.POST.get('iusername_to', '')
        to_user = Person.objects.get(id=to_user_id)
        to_user_username = to_user.username
        from_user_id = user.id
        from_user = user
        if Friendship.objects.are_friends(to_user_id, from_user_id):
            return self.create_response(request, {'success': False, 'message': 'It seems that you are already friends with ' + to_user_username})
        else:
            if from_user == to_user:
                return self.create_response(request, {'success': False, 'message': 'Come on.. you cant add yourself!'})
            else:
                invitations = FriendshipInvitation.objects.invitations(from_user=from_user_id,to_user=to_user_id)
                if (not invitations):
                    FriendshipInvitation.objects.create(from_user=from_user, to_user=to_user, status=1)
                    return self.create_response(request, {'success': True, 'message': 'Hey ' +  user.username + '!' +
                          'You successfully sent invitation to ' + to_user_username})
                else:
                    return self.create_response(request, {'success': False, 'message': 'It seems that there is already a pending invitation for ' + to_user_username})

    def accept(self, request, **kwargs):
        self.is_authenticated(request)
        user = checkRequestAndGetRequester(self, request)
        invitation_id = request.POST.get('invitationID', '')
        if (invitation_id):
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
            except FriendshipInvitation.DoesNotExist:
                invitation = None
            if ((invitation) and (invitation.to_user == user)):
                invitation.accept()
                return self.create_response(request, {'success': True, 'message': 'Successfully Accepted Friend Invitation From User' + invitation.from_user.username})
            else:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

    def decline(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request)
        invitation_id = request.POST.get('invitationID', '')
        if (invitation_id):
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
            except FriendshipInvitation.DoesNotExist:
                invitation = None
            if ((invitation) and (invitation.to_user == person)):
                invitation.decline()
                return self.create_response(request, {'success': True, 'message': 'Successfully Declined Friend Invitation From User ' + person.username})
            else:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())


    def pending(self, request, **kwargs):
        self.is_authenticated(request)
#        person = Person.objects.get(username='Foo')
#        request.user = person
        person = checkRequestAndGetRequester(self, request)
        try:
            invitations = FriendshipInvitation.objects.filter(to_user=person, status=1)
        except FriendshipInvitation.DoesNotExist:
            invitations = None
        if (invitations):
            jsonInvitations = simplejson.dumps([{'userID': invitation.from_user.id, 'username': invitation.from_user.username, 'message': invitation.message,
                'sent': invitation.sent.strftime('%Y-%m-%d'), 'photo': invitation.from_user.photo.url if invitation.from_user.photo else '',
                'date_read': invitation.date_read.strftime('%Y-%m-%d') if invitation.date_read else '', 'id': invitation.id} for invitation in invitations])
            return self.create_response(request, {'success': True, 'invitations': jsonInvitations})
        else:
            return self.create_response(request, {'success': False})

def checkRequestAndGetRequester(caller, request):
    consumer_key = get_oauth_consumer_key_from_header(request.META.get('HTTP_AUTHORIZATION'))
    try:
        consumer = OAuthConsumer.objects.get(key=consumer_key)
    except OAuthConsumer.DoesNotExist:
        consumer = None
    if not consumer:
        raise ImmediateHttpResponse(response=http.HttpUnauthorized())
    else:
        person = Person.objects.get(username=consumer.key)
    if not person:
        raise ImmediateHttpResponse(response=http.HttpUnauthorized())
    else:
        request.user = person
    caller.is_authorized(request)
    return person