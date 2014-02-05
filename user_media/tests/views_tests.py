"""Tests for the views of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.test import TestCase

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewTestMixin

from user_media.tests.factories import (
    DummyGalleryFactory,
    DummyModelFactory,
    UserMediaImageFactory,
)


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
        self.gallery = DummyGalleryFactory()

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
        test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')

        with open(test_file) as fp:
            data = {'image': fp, }
            resp = self.client.post(self.get_url(), data=data)
            self.assertRedirects(
                resp, self.dummy.get_absolute_url(),
                msg_prefix=('When a content object given, view should redirect'
                            ' to the absolute URL of the content object.'))

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

        self.is_not_callable(kwargs={
            'content_type': ContentType.objects.get_for_model(
                self.gallery).model,
            'object_id': self.gallery.pk,
        })


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
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')

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


class EditAndDeleteTestCaseMixin(object):
    """Tests that are the same for both views."""
    def setUp(self):
        self.dummy = DummyModelFactory()
        self.user = self.dummy.user
        self.image = UserMediaImageFactory(user=self.user)
        self.image.content_object = self.dummy
        self.image.save()
        self.image_no_content_object = UserMediaImageFactory(user=self.user)
        self.other_image = UserMediaImageFactory()

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
            "Should return 404 if the user tries to manipulate another user's"
            " object"))

        resp = self.client.post(self.get_url(view_kwargs={'pk': 999}))
        self.assertEqual(resp.status_code, 404, msg=(
            'Should return 404 if the user tries to manipulate a non existing'
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


class DeleteImageViewTestCase(ViewTestMixin, EditAndDeleteTestCaseMixin,
                              TestCase):
    """Tests for the ``DeleteImageView`` generic view class."""
    def get_view_name(self):
        return 'user_media_image_delete'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}


class EditImageViewTestCase(ViewTestMixin, EditAndDeleteTestCaseMixin,
                            TestCase):
    """Tests for the ``EditImageView`` view class."""
    def get_view_name(self):
        return 'user_media_image_edit'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}


class AJAXMultipleImageUploadViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``AJAXMultipleImageUploadView`` generic view class."""
    longMessage = True

    def setUp(self):
        self.profile = DummyModelFactory()
        self.other_profile = DummyModelFactory()
        self.invalid_content_object = UserFactory()
        self.c_type = ContentType.objects.get_for_model(self.profile).model

    def get_view_name(self):
        return 'user_media_ajax_multiple_upload'

    def get_view_kwargs(self):
        return {'c_type': self.c_type, 'obj_id': self.profile.id}

    def upload_to_gallery(self):
        f = open(os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png'))
        kwargs = {'c_type': self.c_type, 'obj_id': self.profile.id}
        self.is_callable('post', {'image': f}, ajax=True, kwargs=kwargs,
                         message=('Upload should be valid.'))
        f.close()

    def test_view(self):
        self.is_not_callable()
        self.is_not_callable(user=self.profile.user,
                             message=('Should only be callable via AJAX.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': 'foo', 'obj_id': self.profile.id},
            message=('Should only be callable, if content type exists.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': self.c_type, 'obj_id': 999},
            message=('Should only be callable, if content object exists.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': self.c_type, 'obj_id': self.other_profile.pk},
            message=('Should only be callable, if the current user owns the'
                     ' chosen profile.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={
                'c_type': ContentType.objects.get_for_model(
                    self.invalid_content_object),
                'obj_id': self.invalid_content_object.pk
            },
            message=("Should only be callable, if the content object is one of"
                     " the user's items."))

        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()

        f = open(os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png'))
        resp = self.is_callable('post', {'image': f}, ajax=True,
                                message=('Upload should be valid.'))
        self.assertEqual(resp.content, 'Maximum amount limit exceeded.', msg=(
            'Should return an error message.'))
        f.close()


class AJAXSingleImageUploadViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``AJAXSingleImageUploadView`` generic view class."""
    longMessage = True

    def setUp(self):
        self.gallery = DummyGalleryFactory()
        self.other_gallery = DummyGalleryFactory()
        self.invalid_content_object = UserFactory()
        self.c_type = ContentType.objects.get_for_model(self.gallery).model

    def get_view_name(self):
        return 'user_media_ajax_single_upload'

    def get_view_kwargs(self):
        return {
            'c_type': self.c_type,
            'obj_id': self.gallery.id,
            'field': 'logo',
        }

    def test_view(self):
        self.is_not_callable()
        self.is_not_callable(method='post', user=self.gallery.user_connection,
                             message=('Should only be callable via AJAX.'))

        logo_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/logo.png')
        with open(logo_file) as f:
            self.is_callable('post', {'logo': f}, ajax=True,
                             message=('Upload should be valid.'))

        new_kwargs = {
            'c_type': 'foo',
            'obj_id': self.gallery.id,
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, method='post', kwargs=new_kwargs,
            message=('Should only be callable, if content type exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': self.gallery.id,
            'field': 'foobar',
        }
        self.is_not_callable(
            ajax=True, method='post', kwargs=new_kwargs,
            message=('Should only be callable, if field exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': '999',
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, method='post', kwargs=new_kwargs,
            message=('Should only be callable, if content object exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': self.other_gallery.pk,
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, method='post', kwargs=new_kwargs,
            message=('Should only be callable, if the current user owns the'
                     ' chosen vendor.'))


class AJAXImageCropViewTestCase(ViewTestMixin, TestCase):
    """Tests for the ``AJAXImageCropView`` generic view class."""
    def setUp(self):
        self.image = UserMediaImageFactory()
        self.image2 = UserMediaImageFactory()

    def get_view_name(self):
        return 'user_media_image_crop'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}

    def test_view(self):
        logo_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/logo.png')
        with open(logo_file) as f:
            self.image.image.save(logo_file, File(f))
            self.image.save()
        self.is_not_callable()
        self.is_not_callable(user=self.image.user)
        data = {'x': 10, 'x2': 15, 'y': 2, 'y2': 10, 'w': 5, 'h': 8}
        self.is_callable(user=self.image.user, method='post', data=data,
                         ajax=True)
        self.is_not_callable(user=self.image2.user, method='post', ajax=True)
