__author__ = 'mpetyx'

"""
    all the basic database schema of crowdit
"""

import datetime
from django_google_maps import fields as map_fields
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

class Person(User):
    photo = models.ImageField(blank=True,upload_to='media/persons')
    class Admin:
        pass

    def getImage(self):
        return "<img src='/%s' width=97 height=72/>" % self.photo.url

    getImage.allow_tags = True

    def __unicode__(self):
        return self.username


class Celebrity(User):
    photo = models.ImageField(blank=True,upload_to='media/celebrities')
    class Admin:
        pass

    def getImage(self):
        return "<img src='/%s' width=97 height=72/>" % self.photo.url

    getImage.allow_tags = True

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
    image = models.ImageField(upload_to='media/events')
    category = models.CharField(max_length=200)
    activationDate = models.DateTimeField('activation date')
    expiryDate = models.DateTimeField('expiry date')
    geolocation = map_fields.GeoLocationField(max_length=100)

    class Meta:
        db_table = "crowdit_event"

    def getImage(self):
        return "<img src='/%s' width=97 height=72/>" % self.image.url

    getImage.allow_tags = True

    def __unicode__(self):
        return u'%s' % (self.title)


class Award(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    points = models.IntegerField(max_length=200)
    numberLeft = models.IntegerField(max_length=10)
    image = models.ImageField(upload_to='media/awards')
    event = models.ForeignKey(Event)

    def getImage(self):
        return "<img src='/%s' width=97 height=72/>" % self.image.url

    getImage.allow_tags = True

    def __unicode__(self):
        return self.title

class OAuthConsumer(models.Model):

    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "api_oauth_consumer"

    def __unicode__(self):
        return u'%s' % (self.name)