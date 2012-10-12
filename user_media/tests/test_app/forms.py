"""Dummy forms for the tests of the `django-user-media` application."""
from django import forms

from user_media.forms import UserMediaImageFormMixin

from user_media.tests.test_app.models import DummyModel


class DummyModelForm(UserMediaImageFormMixin, forms.ModelForm):
    class Meta:
        model = DummyModel
        exclude = ('user', )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(DummyModelForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.user = self.user
        return super(DummyModelForm, self).save(*args, **kwargs)
