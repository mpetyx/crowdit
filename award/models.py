from django.db import models
from djangotoolbox import fields
from event.models import Event



class Award(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    points = models.IntegerField(max_length=200)
    # image = fields.BlobField()
    event = models.ForeignKey(Event)

    def __unicode__(self):
            return self.title

    def getImageUrl(self):
        return '/award/%d' % self.id
