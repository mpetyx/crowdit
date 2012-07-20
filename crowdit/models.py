__author__ = 'mpetyx'

"""
    all the basic database schema of crowdit
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Person(models.Model):

    user = models.OneToOneField(User)
    firstName = models.CharField(max_length=255)
    lastName  = models.CharField(max_length=255)
    mail      = models.EmailField()
    username  = models.CharField(max_length=255)
    added_on = models.DateTimeField(auto_now_add=True)

    class Admin:
        pass

    def __unicode__(self):
        return self.username