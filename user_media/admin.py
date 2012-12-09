"""Admin classes for the ``django-user-media`` app."""
from django.contrib import admin

from user_media.models import UserMediaImage


class UserMediaImageAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'content_type', 'object_id', 'image', )
    list_filter = ('content_type', )
    search_fields = ('user__email', )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'


admin.site.register(UserMediaImage, UserMediaImageAdmin)
