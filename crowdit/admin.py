__author__ = 'mpetyx'

from tastypie.models import ApiAccess, ApiKey
from models import *
from django.contrib import admin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields

class AwardsInline(admin.TabularInline):
    model = Award
    extra = 3

class EventsInline(admin.TabularInline):
    model = Event
    extra = 3

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'category', 'address', 'activationDate', 'expiryDate', 'getImage')
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    inlines = [AwardsInline]

class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')

class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')

class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'getImage')


admin.site.register(Award, AwardAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Celebrity, CelebrityAdmin)
admin.site.register(ApiKey)
admin.site.register(ApiAccess)
admin.site.register(OAuthConsumer)
