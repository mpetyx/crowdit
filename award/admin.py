from award.models import Award
from django.contrib import admin


class AwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'points', 'Image_Preview')

    def Image_Preview(self, obj):
        return "<img src='%s' width=97 height=72/>" % obj.getImageUrl()

    Image_Preview.allow_tags = True

admin.site.register(Award, AwardAdmin)
