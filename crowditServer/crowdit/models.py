"""
    all the basic database schema of crowdit
"""

import datetime
from random import random
from django_google_maps import fields as map_fields
from django.db import models
from django.contrib.auth.models import User
from tastypie.models import create_api_key
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import signals
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.contrib.sites.models import Site
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from hashlib import sha1
import binascii
import hmac
import os


# ###############################
#Credits go to http://djangosnippets.org/snippets/1976/
#and
#http://wavesandmaps.com/utilizing-s3-for-a-heroku-django-app/
# ###############################
class S3Storage(FileSystemStorage):
    def __init__(self, bucket=None, location=None, base_url=None):
        assert bucket
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.bucket = bucket
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        class S3File(File):
            def __init__(self, key):
                self.key = key

            def size(self):
                return self.key.size

            def read(self, *args, **kwargs):
                return self.key.read(*args, **kwargs)

            def write(self, content):
                self.key.set_contents_from_string(content)

            def close(self):
                self.key.close()

        return S3File(Key(self.bucket, name))

    def _save(self, name, content):
        key = Key(self.bucket, name)
        if hasattr(content, 'temporary_file_path'):
            key.set_contents_from_filename(content.temporary_file_path())
        elif isinstance(content, File):
            key.set_contents_from_file(content)
        else:
            key.set_contents_from_string(content)

        return name

    def delete(self, name):
        self.bucket.delete_key(name)

    def exists(self, name):
        return Key(self.bucket, name).exists()

    def listdir(self, path):
        return [key.name for key in self.bucket.list()]

    def path(self, name):
        raise NotImplementedError

    def size(self, name):
        return self.bucket.get_key(name).size

    def url(self, name):
        return Key(self.bucket, name).generate_url(100000)

    def get_available_name(self, name):
        return name


class S3EnabledImageField(models.ImageField):
    def __init__(self, bucket=settings.AWS_STORAGE_BUCKET_NAME, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        self.connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        if not self.connection.lookup(bucket):
            self.connection.create_bucket(bucket)
        self.bucket = self.connection.get_bucket(bucket)
        kwargs['storage'] = S3Storage(self.bucket)
        super(S3EnabledImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)


models.signals.post_save.connect(create_api_key, sender=User)


class Person(User):
    photo = S3EnabledImageField(blank=True, upload_to='media/persons')

    class Admin:
        pass

    def get_image(self):
        return "<img src='%s' width=97 height=72/>" % self.photo.url if self.photo else ''

    get_image.allow_tags = True

    def __unicode__(self):
        return self.username


class Celebrity(User):
    photo = S3EnabledImageField(blank=True, upload_to='media/celebrities')

    class Admin:
        pass

    def get_image(self):
        return "<img src='%s' width=97 height=72/>" % self.photo.url if self.photo else ''

    get_image.allow_tags = True

    def __unicode__(self):
        return self.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Person.objects.get_or_create(user=instance)


class Event(models.Model):
    userCreated = models.ForeignKey(Celebrity)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    address = map_fields.AddressField(max_length=200)
    image = S3EnabledImageField(upload_to='media/events')
    category = models.CharField(max_length=200)
    activationDate = models.DateTimeField('activation date')
    openingDate = models.DateTimeField('opening date', default=datetime.datetime.now())
    expiryDate = models.DateTimeField('expiry date')
    geolocation = map_fields.GeoLocationField(max_length=100)

    class Meta:
        db_table = "crowdit_event"

    def get_image(self):
        return "<img src='%s' width=97 height=72/>" % self.image.url if self.image else ''

    get_image.allow_tags = True

    def __unicode__(self):
        return u'%s' % (self.title)


class Award(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    points = models.IntegerField(max_length=200)
    numberLeft = models.IntegerField(max_length=10)
    image = S3EnabledImageField(upload_to='media/awards')
    event = models.ForeignKey(Event)

    def get_image(self):
        return "<img src='%s' width=97 height=72/>" % self.image.url if self.image else ''

    get_image.allow_tags = True

    def __unicode__(self):
        return self.title


class EventPersonManager(models.Manager):
    def is_person_attending_event(self, person, event):
        eventPersons = self.filter(person=person, event=event)
        if eventPersons:
            return True
        else:
            return False


class EventPerson(models.Model):
    person = models.ForeignKey(Person, related_name='eventperson_person')
    event = models.ForeignKey(Event)
    invitedFrom = models.ForeignKey(Person, related_name='eventperson_invitedFrom', blank=True, null=True)
    isValid = models.BooleanField(default=False)
    objects = EventPersonManager()

    class Meta:
        db_table = "crowdit_event_person"

#    def __unicode__(self):
#        return u'%s' % (self.title)


class OAuthConsumer(models.Model):

    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "api_oauth_consumer"

    def __unicode__(self):
        return u'%s' % (self.name)

# favour django-mailer but fall back to django.core.mail
if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
else:
    from django.core.mail import send_mail

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

if "emailconfirmation" in settings.INSTALLED_APPS:
    from emailconfirmation.models import EmailAddress
else:
    EmailAddress = None


class Contact(models.Model):
    """
    A contact is a person known by a user who may or may not themselves
    be a user.
    """

    # the user who created the contact
    user = models.ForeignKey(Person, related_name="contacts")

    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    added = models.DateField(default=datetime.date.today)

    # the user(s) this contact correspond to
    users = models.ManyToManyField(Person)

    def __unicode__(self):
        return "%s (%s's contact)" % (self.email, self.user)


class FriendshipManager(models.Manager):

    def friends_for_user(self, user):
        friends = []
        for friendship in self.filter(from_user=user).select_related(depth=1):
            friends.append({"friend": friendship.to_user, "friendship": friendship})
        for friendship in self.filter(to_user=user).select_related(depth=1):
            friends.append({"friend": friendship.from_user, "friendship": friendship})
        return friends

    def are_friends(self, user1, user2):
        if self.filter(from_user=user1, to_user=user2).count() > 0:
            return True
        if self.filter(from_user=user2, to_user=user1).count() > 0:
            return True
        return False

    def remove(self, user1, user2):
        if self.filter(from_user=user1, to_user=user2):
            friendship = self.filter(from_user=user1, to_user=user2)
        elif self.filter(from_user=user2, to_user=user1):
            friendship = self.filter(from_user=user2, to_user=user1)
        friendship.delete()


class Friendship(models.Model):
    """
    A friendship is a bi-directional association between two users who
    have both agreed to the association.
    """

    to_user = models.ForeignKey(Person, related_name="friends")
    from_user = models.ForeignKey(Person, related_name="_unused_")
    # @@@ relationship types
    added = models.DateField(default=datetime.date.today)

    objects = FriendshipManager()

    class Meta:
        unique_together = (('to_user', 'from_user'),)


def friend_set_for(user):
    return set([obj["friend"] for obj in Friendship.objects.friends_for_user(user)])


INVITE_STATUS = (
    ("1", "Created"),
    ("2", "Sent"),
    ("3", "Failed"),
    ("4", "Expired"),
    ("5", "Accepted"),
    ("6", "Declined"),
    ("7", "Joined Independently"),
    ("8", "Deleted")
    )


class JoinInvitationManager(models.Manager):

    def send_invitation(self, from_user, to_email, message):
        contact, created = Contact.objects.get_or_create(email=to_email, user=from_user)
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + to_email).hexdigest()

        accept_url = u"http://%s%s" % (
            unicode(Site.objects.get_current()),
            reverse("friends_accept_join", args=(confirmation_key,)),
            )

        ctx = {
            "SITE_NAME": settings.SITE_NAME,
            "CONTACT_EMAIL": settings.CONTACT_EMAIL,
            "user": from_user,
            "message": message,
            "accept_url": accept_url,
            }

        subject = render_to_string("friends/join_invite_subject.txt", ctx)
        email_message = render_to_string("friends/join_invite_message.txt", ctx)

        send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [to_email])
        return self.create(from_user=from_user, contact=contact, message=message, status="2", confirmation_key=confirmation_key)


class JoinInvitation(models.Model):
    """
    A join invite is an invitation to join the site from a user to a
    contact who is not known to be a user.
    """

    from_user = models.ForeignKey(Person, related_name="join_from")
    contact = models.ForeignKey(Contact)
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)
    confirmation_key = models.CharField(max_length=40)

    objects = JoinInvitationManager()

    def accept(self, new_user):
        # mark invitation accepted
        self.status = "5"
        self.save()
        # auto-create friendship
        friendship = Friendship(to_user=new_user, from_user=self.from_user)
        friendship.save()
        # notify
        if notification:
            notification.send([self.from_user], "join_accept", {"invitation": self, "new_user": new_user})
            friends = []
            for user in friend_set_for(new_user) | friend_set_for(self.from_user):
                if user != new_user and user != self.from_user:
                    friends.append(user)
            notification.send(friends, "friends_otherconnect", {"invitation": self, "to_user": new_user})


class FriendshipInvitationManager(models.Manager):

    def invitations(self, *args, **kwargs):
        return self.filter(*args, **kwargs).exclude(status__in=["6", "8"])


class FriendshipInvitation(models.Model):
    """
    A frienship invite is an invitation from one user to another to be
    associated as friends.
    """

    date_read = models.DateTimeField(blank=True, null=True)
    from_user = models.ForeignKey(Person, related_name="invitations_from")
    to_user = models.ForeignKey(Person, related_name="invitations_to")
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)

    objects = FriendshipInvitationManager()

    def accept(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            friendship = Friendship(to_user=self.to_user, from_user=self.from_user)
            friendship.save()
            self.status = "5"
            self.save()
            if notification:
                notification.send([self.from_user], "friends_accept", {"invitation": self})
                notification.send([self.to_user], "friends_accept_sent", {"invitation": self})
                for user in friend_set_for(self.to_user) | friend_set_for(self.from_user):
                    if user != self.to_user and user != self.from_user:
                        notification.send([user], "friends_otherconnect", {"invitation": self, "to_user": self.to_user})

    def decline(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            self.status = "6"
            self.save()


class FriendshipInvitationHistory(models.Model):
    """
    History for friendship invitations
    """

    from_user = models.ForeignKey(Person, related_name="invitations_from_history")
    to_user = models.ForeignKey(Person, related_name="invitations_to_history")
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)


if EmailAddress:
    def new_user(sender, instance, **kwargs):
        if instance.verified:
            for join_invitation in JoinInvitation.objects.filter(contact__email=instance.email):
                if join_invitation.status not in ["5", "7"]:
                    join_invitation.status = "7"
                    join_invitation.save()
                    # notification will be covered below
            for contact in Contact.objects.filter(email=instance.email):
                contact.users.add(instance.user)
                # @@@ send notification

    # only if django-email-notification is installed
    signals.post_save.connect(new_user, sender=EmailAddress)


def delete_friendship(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(to_user=instance.to_user, from_user=instance.from_user)
    for friendship_invitation in friendship_invitations:
        if friendship_invitation.status != "8":
            friendship_invitation.status = "8"
            friendship_invitation.save()


signals.pre_delete.connect(delete_friendship, sender=Friendship)


# moves existing friendship invitation from user to user to FriendshipInvitationHistory before saving new invitation
def friendship_invitation(sender, instance, **kwargs):
    friendship_invitations = FriendshipInvitation.objects.filter(to_user=instance.to_user, from_user=instance.from_user)
    for friendship_invitation in friendship_invitations:
        FriendshipInvitationHistory.objects.create(
            from_user=friendship_invitation.from_user,
            to_user=friendship_invitation.to_user,
            message=friendship_invitation.message,
            sent=friendship_invitation.sent,
            status=friendship_invitation.status
        )
        friendship_invitation.delete()


def get_decrypted_key(string, base):
#    b = string.encode('ascii')
#    a = base.encode('ascii')
    hashedObject = hmac.new(string.encode('ascii'), base.encode('ascii'), sha1)
    return binascii.b2a_base64(hashedObject.digest())[:-1]


def convert_datetime_to_string(o):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

#    if isinstance(o, datetime.date):
#        return o.strftime(DATE_FORMAT)
#    elif isinstance(o, datetime.time):
#        return o.strftime(TIME_FORMAT)
#    elif isinstance(o, datetime.datetime):
    return o.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))

signals.pre_save.connect(friendship_invitation, sender=FriendshipInvitation)