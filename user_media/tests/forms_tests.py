"""Tests for the forms of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from mixer.backend.django import mixer

from ..forms import UserMediaImageForm, UserMediaImageSingleUploadForm
from .test_app.forms import DummyModelForm


class UserMediaImageFormMixinTestCase(TestCase):
    """Tests for the ``UserMediaImageFormMixin`` form mixin."""
    def test_mixin(self):
        self.test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')
        with open(self.test_file) as f:
            form = DummyModelForm(
                instance=mixer.blend('test_app.DummyModel'),
                data={'user': mixer.blend('auth.User').pk},
                files={'images': SimpleUploadedFile(f.name, f.read())})
            self.assertTrue(form.is_valid(), msg=(
                'Should be valid, but returned: {}'.format(
                    form.errors.items())))
            form.save()


class UserMediaImageFormTestCase(TestCase):
    """Tests for the ``UserMediaImageForm`` model form."""

    def test_form(self):
        self.test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')
        with open(self.test_file) as f:
            form = UserMediaImageForm(
                mixer.blend('auth.User'), None, None,
                files={'image': SimpleUploadedFile(f.name, f.read())})
            self.assertTrue(form.is_valid(), msg=(
                'Should be valid but returned: %s' % form.errors.items()))
            result = form.save()
            self.assertTrue('.png' in result.image.url)


class UserMediaImageSingleUploadFormTestCase(TestCase):
    """Tests for the ``UserMediaImageSingleUploadForm`` model."""
    longMessage = True

    def test_form(self):
        form = UserMediaImageSingleUploadForm(
            instance=mixer.blend('test_app.DummyModel'), image_field='image',
            data={})
        self.assertFalse(form.is_valid())
