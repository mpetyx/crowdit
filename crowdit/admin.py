from tastypie.models import ApiAccess, ApiKey
from models import *
from django.contrib import admin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields


class AwardsInline(admin.TabularInline):
    model = Award
    extra = 3

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'category', 'address', 'activationDate', 'expiryDate', 'getImage')
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    readonly_fields = ('userCreated',)
    inlines = [AwardsInline]

    def queryset(self, request):
        qs = super(EventAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(userCreated=request.user)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            celebrity = Celebrity.objects.get(id=request.user.id)
            obj.userCreated = celebrity
        obj.save()

#    def save_formset(self, request, form, formset, change):
#        if formset.model == Award and not request.user.is_superuser:
#            instances = formset.save(commit=False)
#            for instance in instances:
#                celebrity = Celebrity.objects.get(id=request.user.id)
#                instance.userCreated = celebrity
#                instance.save()
#        else:
#            formset.save()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return self.readonly_fields

class EventPersonAdmin(admin.ModelAdmin):
    list_display = ('event', 'person', 'invitedFrom')


class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')


class CelebrityAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'getImage')


class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'getImage')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event" and not request.user.is_superuser:
            kwargs["queryset"] = Event.objects.filter(userCreated=request.user)
            return db_field.formfield(**kwargs)
        return super(AwardAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        qs = super(AwardAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(event__userCreated=request.user)


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
