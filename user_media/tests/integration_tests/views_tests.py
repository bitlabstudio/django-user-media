"""Tests for the views of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from user_media.tests.factories import UserMediaImageFactory


class CreateImageViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``CreateImageView`` generic view class."""
    def setUp(self):
        self.user = UserFactory()

    def get_view_name(self):
        return 'user_media_image_create'

    def get_view_kwargs(self):
        return {
            'content_type': '',
            'object_id': '',
        }

    def test_view(self):
        self.should_be_callable_when_authenticated(self.user)

        # TODO 'Should return 404 when the object does not exist'))

        # TODO "Should return 404 when trying to access another user's object"

        test_file = test_file = os.path.join(
            settings.PROJECT_ROOT, 'test_media/car.png')
        with open(test_file) as fp:
            data = {'image': fp, 'next': '/'}
            resp = self.client.post(self.get_url(), data=data)
            self.assertRedirects(resp, '/')


class DeleteImageViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``DeleteImageView`` generic view class."""
    def setUp(self):
        self.image = UserMediaImageFactory()
        self.other_image = UserMediaImageFactory()
        self.user = self.image.user

    def get_view_name(self):
        return 'user_media_image_delete'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}

    def test_view(self):
        self.login(self.user)
        resp = self.client.post(self.get_url())
        # TODO
        #        "Should redirect to the content object's absolute url after"
        #        " deleting the image"

        # TODO
        #    "Should return 404 if the user tries to delete another user's"
        #    " object"

        # TODO
        #    "Should return 404 if the user tries to delete a non existing"
        #    " object"
