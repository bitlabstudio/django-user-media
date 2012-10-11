"""Forms for the ``django-user-media`` app."""
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from user_media.models import UserMediaImage


class UserMediaImageFormMixin(object):
    """TODO: Write docs"""

    image_label = _('Image')
    require_user_media_image = False

    def __init__(self, *args, **kwargs):
        super(UserMediaImageFormMixin, self).__init__(*args, **kwargs)
        self.fields['user_media_image'] = forms.ImageField(
            required=self.require_user_media_image,
            label=self.image_label,
        )

    def save(self, *args, **kwargs):
        instance = super(UserMediaImageFormMixin, self).save(*args, **kwargs)
        umedia_image = self.cleaned_data['user_media_image']
        if umedia_image:
            image = UserMediaImage()
            image.user = instance.user
            image.content_type = ContentType.objects.get_for_model(
                instance)
            image.object_id = instance.pk
            image.image = umedia_image
            image.save()
        return instance


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
