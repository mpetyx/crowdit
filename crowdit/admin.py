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


class EventPersonAdmin(admin.ModelAdmin):
    list_display = ('event', 'person', 'invitedFrom')


class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')


class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')


class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'getImage')


class ContactAdmin(admin.ModelAdmin):
        list_display = ('id', 'name', 'email', 'user', 'added')


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'added',)


class JoinInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'contact', 'status')


class FriendshipInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'sent', 'status',)


class FriendshipInvitationHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'sent', 'status',)


admin.site.register(Contact, ContactAdmin)
admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(JoinInvitation, JoinInvitationAdmin)
admin.site.register(FriendshipInvitation, FriendshipInvitationAdmin)
admin.site.register(FriendshipInvitationHistory, FriendshipInvitationHistoryAdmin)

admin.site.register(EventPerson, EventPersonAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Celebrity, CelebrityAdmin)
admin.site.register(ApiKey)
admin.site.register(ApiAccess)
admin.site.register(OAuthConsumer)
