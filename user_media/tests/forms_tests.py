"""Tests for the forms of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from django_libs.tests.factories import UserFactory

from user_media.forms import UserMediaImageForm
from user_media.tests.test_app.forms import DummyModelForm


class UserMediaImageFormTestCaseMixin(object):
    """Mixin for test cases that deal with user media image forms."""
    def setUp(self):
        self.user = UserFactory()
        self.test_file = os.path.join(
            settings.PROJECT_ROOT, 'test_media/img.png')
        self.img = open(self.test_file)
        self.uploaded = SimpleUploadedFile(self.img.name, self.img.read())


class UserMediaImageFormMixinTestCase(UserMediaImageFormTestCaseMixin,
                                      TestCase):
    """Tests for the ``UserMediaImageFormMixin`` form mixin."""
    def test_mixin(self):
        form = DummyModelForm(self.user,
            files={'user_media_image': self.uploaded})
        self.assertTrue(form.is_valid(), msg=(
            'Should be valid but returned: %s' % form.errors.items()))
        result = form.save()
        self.assertTrue('.png' in result.image.image.url)


class UserMediaImageFormTestCase(UserMediaImageFormMixinTestCase, TestCase):
    """Tests for the ``UserMediaImageForm`` model form."""

    def test_form(self):
        form = UserMediaImageForm(self.user, None, None,
            files={'image': self.uploaded})
        self.assertTrue(form.is_valid(), msg=(
            'Should be valid but returned: %s' % form.errors.items()))
        result = form.save()
        self.assertTrue('.png' in result.image.url)
