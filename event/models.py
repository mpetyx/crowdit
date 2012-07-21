from django.db import models
import datetime
from djangotoolbox import fields


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    # image = models.ImageField(upload_to='media')
    category = models.CharField(max_length=200)
    activationDate = models.DateTimeField('activation date')
    expiryDate = models.DateTimeField('expiry date')
    lon = models.FloatField()
    lat = models.FloatField()

    # location = db.GeoPt()

    def __unicode__(self):
            return self.title

    def isExpired(self):
        return self.expiryDate < datetime.datetime.now()
    isExpired.short_description = 'Is Expired?'

    def getImageUrl(self):
        return '/event/%d' % self.id
