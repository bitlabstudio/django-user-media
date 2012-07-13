"""Tests for the forms of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from django_libs.tests.factories import UserFactory

from user_media.forms import UserMediaImageForm


class UserMediaImageFormTestCase(TestCase):
    """Tests for the ``UserMediaImageForm`` model form."""
    def setUp(self):
        self.user = UserFactory()

    def test_form(self):
        test_file = os.path.join(settings.PROJECT_ROOT, 'test_media/img.png')
        img = open(test_file)
        uploaded = SimpleUploadedFile(img.name, img.read())
        form = UserMediaImageForm(self.user, None, None,
            files={'image': uploaded})
        self.assertTrue(form.is_valid(), msg=(
            'Should be valid but returned: %s' % form.errors.items()))
        result = form.save()
        self.assertTrue('.png' in result.image.url)
