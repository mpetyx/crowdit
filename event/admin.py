from event.models import Event
from award.models import Award
from django.contrib import admin


def ImagePreview(obj):
        return "<img src='%s' width=97 height=72/>" % obj.getImageUrl()

ImagePreview.allow_tags = True


class AwardsInline(admin.TabularInline):
        model = Award
        extra = 3


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'category', 'address',
       'activationDate', 'expiryDate', 'lon', 'lat', ImagePreview, 'isExpired')
    inlines = [AwardsInline]


admin.site.register(Event, EventAdmin)
