"""Dummy forms for the tests of the `django-user-media` application."""
from django import forms
from django.utils.translation import ugettext_lazy as _

from user_media.forms import UserMediaImageFormMixin
from user_media.tests.test_app.models import DummyModel


class DummyModelForm(UserMediaImageFormMixin, forms.ModelForm):
    image_label = _('Image')
    require_user_media_image = False
    image_field_name = 'images'

    class Meta:
        model = DummyModel
        fields = ('user', )
