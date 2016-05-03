"""Tests for the forms of the ``django-user-media`` app."""
from django.test import TestCase

from mixer.backend.django import mixer, get_image

from ..forms import UserMediaImageForm, UserMediaImageSingleUploadForm
from .test_app.forms import DummyModelForm


class UserMediaImageFormMixinTestCase(TestCase):
    """Tests for the ``UserMediaImageFormMixin`` form mixin."""
    def test_mixin(self):
        form = DummyModelForm(
            instance=mixer.blend('test_app.DummyModel'),
            data={'user': mixer.blend('auth.User').pk},
            files={'images': get_image()})
        self.assertTrue(form.is_valid(), msg=(
            'Should be valid, but returned: {}'.format(
                form.errors.items())))
        form.save()


class UserMediaImageFormTestCase(TestCase):
    """Tests for the ``UserMediaImageForm`` model form."""
    longMessage = True

    def test_form(self):
        form = UserMediaImageForm(
            mixer.blend('auth.User'), None, None,
            files={'image': get_image()})
        self.assertTrue(form.is_valid(), msg=(
            'Should be valid but returned: %s' % form.errors.items()))
        result = form.save()
        self.assertIn('.jpg', result.image.url)


class UserMediaImageSingleUploadFormTestCase(TestCase):
    """Tests for the ``UserMediaImageSingleUploadForm`` model."""
    longMessage = True

    def test_form(self):
        form = UserMediaImageSingleUploadForm(
            instance=mixer.blend('test_app.DummyModel'), image_field='image',
            data={})
        self.assertFalse(form.is_valid())
