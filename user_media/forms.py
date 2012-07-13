"""Forms for the ``django-user-media`` app."""
from django import forms

from user_media.models import UserMediaImage


class UserMediaImageForm(forms.ModelForm):
    class Meta:
        model = UserMediaImage
        exclude = ('user', 'content_type', 'object_id')

    def __init__(self, user, content_type, object_id, *args, **kwargs):
        self.user = user
        self.content_type = content_type
        self.object_id = object_id
        super(UserMediaImageForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.user = self.user
        self.instance.content_type = self.content_type
        self.instance.object_id = self.object_id
        return super(UserMediaImageForm, self).save(*args, **kwargs)
