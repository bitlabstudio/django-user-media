"""Forms for the ``django-user-media`` app."""
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from user_media.models import UserMediaImage


class UserMediaImageFormMixin(object):
    """
    Adds an `forms.ImageField` with name `user_media_image` to the form.

    Overrides `save()` and makes sure that the uploaded image get's tied
    to the content object instance.

    This is useful if you have a model form for your content object and you
    want to support uploading the user media image right from that form.

    Please make sure that your content object has a property called `user` that
    returns the user to which the content object belongs to.

    Currently it only supports one image per content object. On each subsequent
    upload, all other images of that content object will be deleted before the
    new image will be saved.

    The field name of the ImageField can be overridden by setting
    ``image_field_name`` on the form, that includes this mixin.

    """

    image_label = _('Image')
    require_user_media_image = False
    image_field_name = 'user_media_image'
    image_widget = forms.ClearableFileInput()

    def __init__(self, *args, **kwargs):
        super(UserMediaImageFormMixin, self).__init__(*args, **kwargs)
        try:
            initial_image = getattr(
                self.instance, self.image_field_name).order_by(
                    '-id')[0].image
        except IndexError:
            initial_image = None
        self.fields[self.image_field_name] = forms.ImageField(
            required=self.require_user_media_image,
            label=self.image_label,
            initial=initial_image,
            widget=self.image_widget,
        )

    def _delete_images(self, instance):
        """Deletes all user media images of the given instance."""
        UserMediaImage.objects.filter(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
            user=instance.user,
        ).delete()

    def save(self, *args, **kwargs):
        instance = super(UserMediaImageFormMixin, self).save(*args, **kwargs)
        umedia_image = self.cleaned_data[self.image_field_name]
        if umedia_image:
            self._delete_images(instance)
            image = UserMediaImage()
            image.user = instance.user
            image.content_type = ContentType.objects.get_for_model(
                instance)
            image.object_id = instance.pk
            image.image = umedia_image
            image.save()
        return instance


class UserMediaImageForm(forms.ModelForm):
    """Form that allows to create or update an `UserMediaImage` object."""
    class Meta:
        model = UserMediaImage
        fields = ('image', )

    def __init__(self, user, content_type=None, object_id=None,
                 *args, **kwargs):
        self.user = user
        self.content_type = content_type
        self.object_id = object_id
        if content_type is not None and object_id is not None:
            self.content_object = content_type.get_object_for_this_type(
                pk=self.object_id)
        super(UserMediaImageForm, self).__init__(*args, **kwargs)

    def clean_image(self):
        """
        It seems like in Django 1.5 something has changed.

        When Django tries to validate the form, it checks if the generated
        filename fit into the max_length. But at this point, self.instance.user
        is not yet set so our filename generation function cannot create
        the new file path because it needs the user id. Setting
        self.instance.user at this point seems to work as a workaround.

        """
        self.instance.user = self.user
        data = self.cleaned_data.get('image')
        return data

    def save(self, *args, **kwargs):
        self.instance.user = self.user
        if self.content_type is not None and self.object_id is not None:
            self.instance.content_type = self.content_type
            self.instance.object_id = self.object_id
        return super(UserMediaImageForm, self).save(*args, **kwargs)


class UserMediaImageSingleUploadForm(forms.ModelForm):
    """Form to save a single image upload."""
    def __init__(self, image_field, *args, **kwargs):
        self._meta.model = type(kwargs['instance'])
        super(UserMediaImageSingleUploadForm, self).__init__(*args, **kwargs)
        self.fields[image_field] = forms.ImageField()
