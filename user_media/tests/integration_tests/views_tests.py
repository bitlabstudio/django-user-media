"""Tests for the views of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from user_media.tests.factories import DummyModelFactory, UserMediaImageFactory


class CreateImageViewTestCase(ViewTestMixin, TestCase):
    """
    Tests for the ``CreateImageView`` generic view class.

    Tests the case when the view is called without content type and object
    id.

    """
    def setUp(self):
        self.dummy = DummyModelFactory()
        self.user = self.dummy.user
        self.other_dummy = DummyModelFactory()

    def get_view_name(self):
        return 'user_media_image_create'

    def get_view_kwargs(self):
        ctype = ContentType.objects.get_for_model(self.dummy)
        return {
            'content_type': ctype.model,
            'object_id': self.dummy.pk,
        }

    def test_view(self):
        self.should_be_callable_when_authenticated(self.user)
        test_file = test_file = os.path.join(
            settings.PROJECT_ROOT, 'test_media/img.png')

        with open(test_file) as fp:
            data = {'image': fp, }
            resp = self.client.post(self.get_url(), data=data)
            self.assertRedirects(resp, self.dummy.get_absolute_url(),
                msg_prefix=(
                    'When a content object given, view should redirect to the'
                    ' absolute URL of the content object.'))

        with open(test_file) as fp:
            data = {'image': fp, 'next': '/?foo=bar'}
            resp = self.client.post(self.get_url(), data=data)
            self.assertRedirects(resp, '/?foo=bar', msg_prefix=(
                'When a content object and ``next`` in POST data is given,'
                ' view should redirect to the URL given in ``next`` and ignore'
                ' the content object absolute url.'))

        with open(test_file) as fp:
            data = {'image': fp, }
            resp = self.client.post(self.get_url() + '?next=/', data=data)
            self.assertRedirects(resp, '/', msg_prefix=(
                'When a content object and ``next`` in GET data is given,'
                ' view should redirect to the URL given in ``next`` and ignore'
                ' the content object absolute url.'))

        resp = self.client.post(self.get_url(
            view_kwargs={'content_type': 'dummymodel', 'object_id': 999}))
        self.assertEqual(resp.status_code, 404, msg=(
            'Should raise 404 if the content object does not exist'))

        resp = self.client.post(self.get_url(
            view_kwargs={'content_type': 'foobarmodel', 'object_id': 1}))
        self.assertEqual(resp.status_code, 404, msg=(
            'Should raise 404 if the content type does not exist'))

        view_kwargs = {
            'content_type': 'dummymodel',
            'object_id': self.other_dummy.pk
        }
        resp = self.client.post(self.get_url(view_kwargs=view_kwargs))
        self.assertEqual(resp.status_code, 404, msg=(
            "Should raise 404 if the user tries to add an image to another"
            " uers's content object"))


class CreateImageViewNoCtypeTestCase(ViewTestMixin, TestCase):
    """
    Tests for the ``CreateImageView`` generic view class.

    Tests the case when the view is called without content type and object
    id.

    """
    def setUp(self):
        self.user = UserFactory()

    def get_view_name(self):
        return 'user_media_image_create_no_ctype'

    def test_view(self):
        self.should_be_callable_when_authenticated(self.user)
        test_file = test_file = os.path.join(
            settings.PROJECT_ROOT, 'test_media/img.png')

        with open(test_file) as fp:
            data = {'image': fp, 'next': '/?foo=bar'}
            resp = self.client.post(self.get_url(), data=data)
            self.assertRedirects(resp, '/?foo=bar', msg_prefix=(
                'When no content object given, view should redirect to the'
                ' POST data ``next`` which must be given.'))

        with open(test_file) as fp:
            data = {'image': fp, }
            try:
                resp = self.client.post(self.get_url(), data=data)
            except Exception, ex:
                self.assertTrue('No content object' in ex.message, msg=(
                    'If no content object and no ``next`` parameter given,'
                    ' view should raise an exception'))


class DeleteImageViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``DeleteImageView`` generic view class."""
    def setUp(self):
        self.dummy = DummyModelFactory()
        self.user = self.dummy.user
        self.image = UserMediaImageFactory(user=self.user)
        self.image.content_object = self.dummy
        self.image.save()
        self.image_no_content_object = UserMediaImageFactory(user=self.user)
        self.other_image = UserMediaImageFactory()

    def get_view_name(self):
        return 'user_media_image_delete'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}

    def test_view_with_content_object(self):
        self.should_be_callable_when_authenticated(self.user)
        resp = self.client.post(self.get_url())
        self.assertRedirects(resp, self.dummy.get_absolute_url(), msg_prefix=(
            "If the image had a content object, view should redirect to"
            " that object's absolute url"))

        self.image = UserMediaImageFactory(user=self.user)
        resp = self.client.post(self.get_url(), data={'next': '/?foo=bar'})
        self.assertRedirects(resp, '/?foo=bar', msg_prefix=(
            "If the image had a content object and ``next`` in the POST data,"
            " view should redirect to the URL given in ``next`` and ignore"
            " the content object's absolute URL"))

        self.image = UserMediaImageFactory(user=self.user)
        resp = self.client.post(self.get_url() + '?next=/')
        self.assertRedirects(resp, '/', msg_prefix=(
            "If the image had a content object and ``next`` in the GET data,"
            " view should redirect to the URL given in ``next`` and ignore"
            " the content object's absolute URL"))

        resp = self.client.post(self.get_url(
            view_kwargs={'pk': self.other_image.pk}))
        self.assertEqual(resp.status_code, 404, msg=(
            "Should return 404 if the user tries to delete another user's"
            " object"))

        resp = self.client.post(self.get_url(view_kwargs={'pk': 999}))
        self.assertEqual(resp.status_code, 404, msg=(
            'Should return 404 if the user tries to delete a non existing'
            ' object'))

    def test_view_without_content_object(self):
        self.login(self.user)
        data = {'next': '/?foo=bar', }
        resp = self.client.post(self.get_url(
            view_kwargs={'pk': self.image_no_content_object.pk}), data=data)
        self.assertRedirects(resp, '/?foo=bar', msg_prefix=(
            'If the image had no content object, view should redirect to'
            ' the POST data ``next`` that must be given'))

        self.image_no_content_object = UserMediaImageFactory(user=self.user)
        try:
            resp = self.client.post(self.get_url(
                view_kwargs={'pk': self.image_no_content_object.pk}))
        except Exception, ex:
            self.assertTrue('No content object' in ex.message, msg=(
                'If no content object and no ``next`` parameter given,'
                ' view should raise an exception'))
