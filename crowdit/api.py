from django.conf.urls.defaults import patterns, url
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
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
            # person = Person.obj_create(username=bundle.get('username'), password=bundle.get('password'), )
            g = Group.objects.get(name='Crowdit user')
            g.user_set.add(bundle.obj)
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
            url(r"^(?P<resource_name>%s)/profile%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('profile'), name="api_profile"),
        ]


    def search(self, request, **kwargs):
        self.is_authenticated(request)
        checkRequestAndGetRequester(self, request, True)
        username = request.GET['username'];
        if username:
            try:
                person = Person.objects.get(username=username)
            except:
                person = None
            if person:
                url = person.photo.url if person.photo else ''
                return self.create_response(request, {
                    'success': True,
                    'userID': person.id,
                    'user': person.username,
                    'photo': url
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'message': 'User not found'
                })
        else:
            return self.create_response(request, {
                'success': False,
                'message': 'Please provide a username'
            })


    def friends(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
        user_id = request.GET['userID'];
        profile = Person.objects.get(id=user_id)
        friends = friend_set_for(profile)
        if friends:
            jsonFriends = simplejson.dumps([{
                'username': friend.username,
                'id': friend.id,
                'photo': friend.photo.url if friend.photo else ''
            } for friend in friends])
            return self.create_response(request, {
                'success': True,
                'friends': jsonFriends
            })
        else:
            return self.create_response(request, {
                'success': False,
                'message': 'No friends found'
            })

    def profile(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
#        person = Person.objects.get(username='Bar')
#        request.user = person
        user_id = request.GET['userID'];
        profile = Person.objects.get(id=user_id)
        number_of_friends = Friendship.objects.filter(Q(from_user_id=profile.id) | Q(to_user_id=profile.id)).count()
        is_friend = Friendship.objects.are_friends(person.id, profile.id)
        if person.id == profile.id:
            return self.create_response(request, {
                'success': True,
                'pendingInvitations': {
                    'pendingInvitationExists': False,
                    'canAccept': False,
                    'invitationID' : False,
                    'invitationMessage': False
                },
                'profile': {
                    'username': profile.username,
                    'userID': profile.id,
                    'allowEditing': True,
                    'photo': profile.photo.url if profile.photo else '',
                    'numberOfFriends': number_of_friends
                }
            })
        if is_friend:
            return self.create_response(request, {
                'success': True,
                'pendingInvitations': {
                    'pendingInvitationExists': False,
                    'canAccept': False,
                    'invitationID' : False,
                    'invitationMessage': False
                },
                'profile': {
                    'username': profile.username,
                    'userID': profile.id,
                    'allowEditing': False,
                    'isFriend': is_friend,
                    'photo': profile.photo.url if profile.photo else '',
                    'numberOfFriends': number_of_friends
                }
            })
        else:
            try:
                invitation_id = False
                can_accept = False
                pending_invitation_exists = True
                invitation_message = False
                invitation = FriendshipInvitation.objects.get(Q(from_user=person, to_user=profile, status="1") | Q(from_user=profile, to_user=person, status="1"))
            except:
                pending_invitation_exists = False
            if pending_invitation_exists:
                invitation_id = invitation.id
                if invitation.to_user == person:
                    can_accept = True
                    invitation_message = invitation.message
            return self.create_response(request, {
                'success': True,
                'pendingInvitations': {
                    'pendingInvitationExists': pending_invitation_exists,
                    'canAccept': can_accept,
                    'invitationID' : invitation_id,
                    'invitationMessage': invitation_message
                },
                'profile': {
                    'username': profile.username,
                    'userID': profile.id,
                    'isFriend': is_friend,
                    'allowEditing': False,
                    'photo': profile.photo.url if profile.photo else '',
                    'numberOfFriends': number_of_friends
                }
            })

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
                return self.create_response(request, {
                    'success': True,
                    'userID': person.id,
                    'name': user.username,
                    'key': consumer.key,
                    'secret': consumer.secret
                })
            else:
                # Return a 'disabled account' error message
                return self.create_response(request, {
                    'success': False,
                    'message': 'The user is disabled'
                })
        else:
            # Return an 'invalid login' error message.
            return self.create_response(request, {
                'success': False,
                'message': 'Invalid User. Please make sure you inserted the right username-password'
            })


    def prof_picture_upload(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, False)
        uploaded_file = request.FILES['file']
        person.photo.save(str(person.id) + '.jpg', ContentFile(uploaded_file.read()))
        person.save
        return self.create_response(request, {
            'success': True,
            'profilePictureUrl': person.photo.url
        })


    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        logout(request)


class EventResource(ModelResource):

    class Meta:

        object_class = Event
        queryset = Event.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        resource_name = 'event'
        include_resource_uri = False

    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/upcoming%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('upcoming'), name="api_upcoming"),
            ]

    def upcoming(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
        events = Event.objects.filter(Q(**{'expiryDate__gte': datetime.datetime.now()}),Q(**{'activationDate__lte': datetime.datetime.now()}))
#        :
        awards = {}
        for event in events:
            awards[event.id]=Award.objects.filter(event_id=event.id)
        if events:
            jsonEvents = simplejson.dumps([{
                'id': event.id,
                'category': event.category,
                'title': event.title,
                'userCreated': {
                    'id': event.userCreated.id,
                    'username': event.userCreated.username,
                    'photo': event.userCreated.photo.url if event.userCreated.photo else '',
                },
                'attending': EventPerson.objects.isPersonAttendingEvent(person, event),
                'photo': event.image.url if event.image else '',
                'activationDate': convertDatetimeToString(event.activationDate),
                'expiryDate': convertDatetimeToString(event.expiryDate),
                'openingDate': convertDatetimeToString(event.openingDate),
                'geolocation': {
                    'lat': event.geolocation.lat,
                    'lon': event.geolocation.lon
                },
                'address': event.address,
                'description': event.description,
                'awards': simplejson.dumps([{
                    'title': award.title,
                    'description': award.description,
                    'points': award.points,
                    'numberLeft':award.numberLeft,
                    'photo': award.image.url if award.image else ''
                }
                for award in awards[event.id]])
            } for event in events])
            return self.create_response(request, {
                'success': True,
                'events': jsonEvents
            })
        else:
            return self.create_response(request, {
                'success': False,
                'message': 'No events found'
            })

class EventPersonResource(ModelResource):

    class Meta:

        object_class = EventPerson
        queryset = EventPerson.objects.all()
        list_allowed_methods = ['get', 'post']
        include_resource_uri = False
        resource_name = 'event-person'
        include_resource_uri = False

    def override_urls(self):

        return [
            url(r"^(?P<resource_name>%s)/attend%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('attend'), name="api_attend"),
            url(r"^(?P<resource_name>%s)/unattend%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('unattend'), name="api_unattend"),
            ]

    def attend(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, False)
        eventID = request.POST['eventID']
        try:
            invitedFromID = request.POST['invitedFromID', '']
        except:
            invitedFromID = False
        try:
            event = Event.objects.get(id=eventID)
        except:
            return self.create_response(request, {
                'success': False,
                'message': 'Invalid event submitted'
            })
        if invitedFromID:
            try:
                invitedFrom = Person.objects.get(id=invitedFromID)
            except:
                invitedFrom = False
            if invitedFrom:
                eventPersons = EventPerson.objects.filter(Q(**{'person': person}),Q(**{'event': event}),Q(**{'invitedFrom': invitedFrom}))
            else:
                return self.create_response(request, {
                    'success': False,
                    'message': 'Invalid "invited from" crowd it user'
                })
        else:
            eventPersons = EventPerson.objects.filter(Q(**{'person': person}),Q(**{'event': event}))
        if eventPersons:
            if invitedFromID:
                eventPersons.invitedFrom=invitedFrom
                eventPersons.save()
            else:
                return self.create_response(request, {
                    'success': False,
                    'message': 'You already submitted this request'
                })
        else:
            if invitedFromID:
                EventPerson.objects.create(person=person, invitedFrom=invitedFrom, event=event)
            else:
                EventPerson.objects.create(person=person, event=event)
        return self.create_response(request, {
            'success': True,
            'message': 'Your request was submitted successfully'
        })

    def unattend(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, False)
        eventID = request.POST['eventID']
        try:
            invitedFromID = request.POST['invitedFromID', '']
        except:
            invitedFromID = False
        try:
            event = Event.objects.get(id=eventID)
        except:
            return self.create_response(request, {
                'success': False,
                'message': 'Invalid event submitted'
            })
        if invitedFromID:
            try:
                invitedFrom = Person.objects.get(id=invitedFromID)
            except:
                invitedFrom = False
            if invitedFrom:
                eventPersons = EventPerson.objects.filter(Q(**{'person': person}),Q(**{'event': event}),Q(**{'invitedFrom': invitedFrom}))
            else:
                return self.create_response(request, {
                    'success': False,
                    'message': 'Invalid "invited from" crowd it user'
                })
        else:
            eventPersons = EventPerson.objects.filter(Q(**{'person': person}),Q(**{'event': event}))
        if eventPersons:
            eventPersons[0].delete()
            return self.create_response(request, {
                'success': True,
                'message': 'Successfully unattended the event'
            })
        else:
            return self.create_response(request, {
                'success': False,
                'message': 'It seems you have already unattended this event'
            })

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
            url(r"^(?P<resource_name>%s)/cancel%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('cancel'), name="api_cancel"),
            url(r"^(?P<resource_name>%s)/pending%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('pending'), name="api_pending"),
            url(r"^(?P<resource_name>%s)/read%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('read'), name="api_read"),
            ]


    def read(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
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
                    return self.create_response(request, {
                        'success': False,
                        'message': 'Come on stop trying to hack this app!'
                    })
            return self.create_response(request, {
                'success': True
            })
        elif (invitation):
            if invitation.to_user == person:
                invitation.date_read = datetime.datetime.now()
                invitation.save()
                return self.create_response(request, {
                    'success': True
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'message': 'Come on stop trying to hack this app!'
                })
        else:
            return self.create_response(request, {
                'success': False,
                'message': 'No invitations found!'
            })


    def send(self, request, **kwargs):
        self.is_authenticated(request)
        user = checkRequestAndGetRequester(self, request, True)
        #        the code below will work perfect when the line above will be uncommented and the two lines below will be commented
#        user = Person.objects.get(username='Johnecon')
#        request.user = user

        to_user_id = request.POST.get('iusername_to', '')
        to_user = Person.objects.get(id=to_user_id)
        to_user_username = to_user.username
        from_user_id = user.id
        from_user = user
        if Friendship.objects.are_friends(to_user_id, from_user_id):
            return self.create_response(request, {
                'success': False,
                'message': 'It seems that you are already friends with ' + to_user_username
            })
        else:
            if from_user == to_user:
                return self.create_response(request, {
                    'success': False,
                    'message': 'Come on.. you cant add yourself!'
                })
            else:
                invitations = FriendshipInvitation.objects.invitations(from_user=from_user_id,to_user=to_user_id)
                if (not invitations):
                    FriendshipInvitation.objects.create(from_user=from_user, to_user=to_user, status=1)
                    return self.create_response(request, {
                        'success': True,
                        'message': 'Hey ' +  user.username + '!' + 'You successfully sent invitation to ' + to_user_username
                    })
                else:
                    return self.create_response(request, {
                        'success': False,
                        'message': 'It seems that there is already a pending invitation for ' + to_user_username
                    })

    def accept(self, request, **kwargs):
        self.is_authenticated(request)
        user = checkRequestAndGetRequester(self, request, True)
        invitation_id = request.POST.get('invitationID', '')
        if (invitation_id):
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
            except FriendshipInvitation.DoesNotExist:
                invitation = None
            if ((invitation) and (invitation.to_user == user)):
                invitation.accept()
                return self.create_response(request, {
                    'success': True,
                    'message': 'Successfully Accepted Friend Invitation From User ' + invitation.from_user.username
                })
            else:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())


    def decline(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
        invitation_id = request.POST.get('invitationID', '')
        if (invitation_id):
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
            except FriendshipInvitation.DoesNotExist:
                invitation = None
            if ((invitation) and (invitation.to_user == person)):
                invitation.decline()
                return self.create_response(request, {
                    'success': True,
                    'message': 'Successfully Declined Friend Invitation From User ' + person.username
                })
            else:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())


    def cancel(self, request, **kwargs):
        self.is_authenticated(request)
        person = checkRequestAndGetRequester(self, request, True)
        invitation_id = request.POST.get('invitationID', '')
        if (invitation_id):
            try:
                invitation = FriendshipInvitation.objects.get(id=invitation_id)
            except FriendshipInvitation.DoesNotExist:
                invitation = None
            if ((invitation) and (invitation.from_user == person)):
                invitation.delete()
                return self.create_response(request, {
                    'success': True,
                    'message': 'Successfully Cancelled Friend Invitation To User ' + person.username
                })
            else:
                raise ImmediateHttpResponse(response=http.HttpUnauthorized())
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())


    def pending(self, request, **kwargs):
        self.is_authenticated(request)
#        person = Person.objects.get(username='Foo')
#        request.user = person
        person = checkRequestAndGetRequester(self, request, True)
        try:
            invitations = FriendshipInvitation.objects.filter(to_user=person, status=1)
        except FriendshipInvitation.DoesNotExist:
            invitations = None
        if (invitations):
            jsonInvitations = simplejson.dumps([{
                'userID': invitation.from_user.id,
                'username': invitation.from_user.username,
                'message': invitation.message,
                'sent': invitation.sent.strftime('%Y-%m-%d'),
                'photo': invitation.from_user.photo.url if invitation.from_user.photo else '',
                'date_read': invitation.date_read.strftime('%Y-%m-%d') if invitation.date_read else '',
                'id': invitation.id
            } for invitation in invitations])
            return self.create_response(request, {
                'success': True,
                'found': True,
                'invitations': jsonInvitations
            })
        else:
            return self.create_response(request, {
                'success': True,
                'found': False
            })

def checkRequestAndGetRequester(caller, request, shouldUseGenericAuthorization):
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
    if shouldUseGenericAuthorization:
        caller.is_authorized(request)
        return person
    else:
        crowdit_group = Group.objects.get(name='Crowdit user')
        if request.user.groups.filter(id=crowdit_group.id).exists():
            return person
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
