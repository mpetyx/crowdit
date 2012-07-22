__author__ = 'mpetyx'

"""
    all the basic database schema of crowdit
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

class Person(User):

#    user = models.OneToOneField(User)
#    firstName = models.CharField(max_length=255)
#    lastName  = models.CharField(max_length=255)
#    mail      = models.EmailField()
    # username  = models.CharField(max_length=255)
    # added_on = models.DateTimeField(auto_now_add=True)

    class Admin:
        pass

    def __unicode__(self):
        return self.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Person.objects.get_or_create(user=instance)

class OAuthConsumer(models.Model):

    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "api_oauth_consumer"

    def __unicode__(self):
        return u'%s' % (self.name)