"""Tests for the views of the ``django-user-media`` app."""
import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from django_libs.tests.mixins import ViewRequestFactoryTestMixin
from mixer.backend.django import mixer

from .. import views


class CreateImageViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """
    Tests for the ``CreateImageView`` generic view class.

    Tests the case when the view is called without content type and object
    id.

    """
    view_class = views.CreateImageView

    def setUp(self):
        self.dummy = mixer.blend('test_app.DummyModel')
        self.user = self.dummy.user
        self.other_dummy = mixer.blend('test_app.DummyModel')
        self.gallery = mixer.blend('test_app.DummyGallery')

    def get_view_name(self):
        return 'user_media_image_create'

    def get_view_kwargs(self):
        ctype = ContentType.objects.get_for_model(self.dummy)
        return {
            'content_type': ctype.model,
            'object_id': self.dummy.pk,
        }

    def test_view(self):
        self.is_callable(self.user)
        test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')

        with open(test_file) as fp:
            data = {'image': fp, }
            self.is_postable(user=self.user, data=data,
                             to=self.dummy.get_absolute_url())

        with open(test_file) as fp:
            data = {'image': fp, 'next': '/?foo=bar'}
            self.is_postable(user=self.user, data=data, to='/?foo=bar')

        with open(test_file) as fp:
            data = {'image': fp, }
            self.is_postable(user=self.user, data=data, to='/?foo=bar')

        self.is_not_callable(post=True, user=self.user, kwargs={
            'content_type': 'dummymodel', 'object_id': 999})

        self.is_not_callable(post=True, user=self.user, kwargs={
            'content_type': 'foobarmodel', 'object_id': 1})

        self.is_not_callable(post=True, user=self.user, kwargs={
            'content_type': 'dummymodel',
            'object_id': self.other_dummy.pk
        })

        self.is_not_callable(user=self.user, kwargs={
            'content_type': ContentType.objects.get_for_model(
                self.gallery).model,
            'object_id': self.gallery.pk,
        })


class CreateImageViewNoCtypeTestCase(ViewRequestFactoryTestMixin, TestCase):
    """
    Tests for the ``CreateImageView`` generic view class.

    Tests the case when the view is called without content type and object
    id.

    """
    view_class = views.CreateImageView

    def setUp(self):
        self.user = mixer.blend('auth.User')

    def get_view_name(self):
        return 'user_media_image_create_no_ctype'

    def test_view(self):
        self.is_callable(self.user)
        test_file = test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')

        with open(test_file) as fp:
            data = {'image': fp, 'next': '/?foo=bar'}
            self.is_postable(user=self.user, to='/?foo=bar', data=data)

        with open(test_file) as fp:
            data = {'image': fp, }
            try:
                self.is_postable(user=self.user, data=data)
            except Exception, ex:
                self.assertTrue('No content object' in ex.message, msg=(
                    'If no content object and no ``next`` parameter given,'
                    ' view should raise an exception'))


class EditAndDeleteTestCaseMixin(object):
    """Tests that are the same for both views."""
    def setUp(self):
        self.dummy = mixer.blend('test_app.DummyModel')
        self.user = self.dummy.user
        self.image = mixer.blend('user_media.UserMediaImage', user=self.user)
        self.image.content_object = self.dummy
        logo_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/logo.png')
        with open(logo_file) as f:
            self.image.image.save(logo_file, File(f))
            self.image.save()
        self.image_no_content_object = mixer.blend(
            'user_media.UserMediaImage', user=self.user)
        self.other_image = mixer.blend('user_media.UserMediaImage')

    def test_view_with_content_object(self):
        self.is_callable(self.user)
        self.is_postable(
            user=self.user, to=self.dummy.get_absolute_url(), msg=(
                "If the image had a content object, view should redirect to "
                "that object's absolute url"))

        self.image = mixer.blend('user_media.UserMediaImage', user=self.user)
        self.is_postable(
            user=self.user, data={'next': '/?foo=bar'}, to='/?foo=bar', msg=(
                "If the image had a content object and ``next`` in the POST"
                " data, view should redirect to the URL given in ``next`` and"
                " ignore the content object's absolute URL"))

        self.is_not_callable(
            user=self.user, kwargs={'pk': self.other_image.pk}, post=True,
            msg=("If the image had a content object and ``next`` in the POST"
                 " data, view should redirect to the URL given in ``next`` and"
                 " ignore the content object's absolute URL"))

        self.is_not_callable(
            user=self.user, kwargs={'pk': 999}, post=True,
            msg=('Should return 404 if the user tries to manipulate a non'
                 ' existing object'))

    def test_view_without_content_object(self):
        self.is_postable(
            user=self.user, to='/?foo=bar', data={'next': '/?foo=bar'},
            kwargs={'pk': self.image_no_content_object.pk}, msg=(
                'If the image had no content object, view should redirect to'
                ' the POST data ``next`` that must be given'))

        self.image_no_content_object = mixer.blend(
            'user_media.UserMediaImage', user=self.user)
        try:
            self.is_postable(
                user=self.user, to='/?foo=bar', data={'next': '/?foo=bar'},
                kwargs={'pk': self.image_no_content_object.pk})
        except Exception, ex:
            self.assertTrue('No content object' in ex.message, msg=(
                'If no content object and no ``next`` parameter given,'
                ' view should raise an exception'))


class DeleteImageViewTestCase(ViewRequestFactoryTestMixin,
                              EditAndDeleteTestCaseMixin, TestCase):
    """Tests for the ``DeleteImageView`` generic view class."""
    view_class = views.DeleteImageView

    def get_view_name(self):
        return 'user_media_image_delete'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}


class UpdateImageViewTestCase(ViewRequestFactoryTestMixin,
                              EditAndDeleteTestCaseMixin, TestCase):
    """Tests for the ``UpdateImageView`` view class."""
    view_class = views.UpdateImageView

    def get_view_name(self):
        return 'user_media_image_edit'

    def get_view_kwargs(self):
        return {'pk': self.image.pk}


class AJAXMultipleImageUploadViewTestCase(ViewRequestFactoryTestMixin,
                                          TestCase):
    """Tests for the ``AJAXMultipleImageUploadView`` generic view class."""
    view_class = views.AJAXMultipleImageUploadView

    def setUp(self):
        self.profile = mixer.blend('test_app.DummyModel')
        self.other_profile = mixer.blend('test_app.DummyModel')
        self.invalid_content_object = mixer.blend('auth.User')
        self.c_type = ContentType.objects.get_for_model(self.profile).model

    def get_view_name(self):
        return 'user_media_ajax_multiple_upload'

    def get_view_kwargs(self):
        return {'c_type': self.c_type, 'obj_id': self.profile.id}

    def upload_to_gallery(self):
        test_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png')
        with open(test_file) as fp:
            self.file = SimpleUploadedFile('img.png', '')
            self.file.file = fp
            kwargs = {'c_type': self.c_type, 'obj_id': self.profile.id}
            self.is_postable(
                data={'image': self.file}, ajax=True, user=self.profile.user,
                kwargs=kwargs, msg=('Upload should be valid.'))

    def test_view(self):
        self.is_not_callable(user=self.profile.user,
                             msg=('Should only be callable via AJAX.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': 'foo', 'obj_id': self.profile.id},
            msg=('Should only be callable, if content type exists.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': self.c_type, 'obj_id': 999},
            msg=('Should only be callable, if content object exists.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={'c_type': self.c_type, 'obj_id': self.other_profile.pk},
            msg=('Should only be callable, if the current user owns the'
                 ' chosen profile.'))

        self.is_not_callable(
            user=self.profile.user, ajax=True,
            kwargs={
                'c_type': ContentType.objects.get_for_model(
                    self.invalid_content_object),
                'obj_id': self.invalid_content_object.pk
            },
            msg=("Should only be callable, if the content object is one of"
                 " the user's items."))

        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()
        self.upload_to_gallery()

        f = open(os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/img.png'))
        resp = self.is_postable(
            data={'image': f}, ajax=True, user=self.profile.user,
            msg=('Upload should be valid.'))
        self.assertEqual(resp.content, 'Maximum amount limit exceeded.', msg=(
            'Should return an error message.'))
        f.close()


class AJAXSingleImageUploadViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``AJAXSingleImageUploadView`` generic view class."""
    view_class = views.AJAXSingleImageUploadView

    def setUp(self):
        self.gallery = mixer.blend('test_app.DummyGallery')
        self.other_gallery = mixer.blend('test_app.DummyGallery')
        self.invalid_content_object = mixer.blend('auth.User')
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
        self.is_not_callable(post=True, user=self.gallery.user_connection,
                             msg=('Should only be callable via AJAX.'))

        logo_file = os.path.join(
            settings.DJANGO_PROJECT_ROOT, 'tests/test_media/logo.png')
        with open(logo_file) as f:
            self.is_postable(
                data={'logo': f}, ajax=True, user=self.gallery.user_connection,
                msg=('Upload should be valid.'))

        new_kwargs = {
            'c_type': 'foo',
            'obj_id': self.gallery.id,
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, post=True, kwargs=new_kwargs,
            user=self.gallery.user_connection,
            msg=('Should only be callable, if content type exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': self.gallery.id,
            'field': 'foobar',
        }
        self.is_not_callable(
            ajax=True, post=True, kwargs=new_kwargs,
            user=self.gallery.user_connection,
            msg=('Should only be callable, if field exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': '999',
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, post=True, kwargs=new_kwargs,
            user=self.gallery.user_connection,
            msg=('Should only be callable, if content object exists.'))

        new_kwargs = {
            'c_type': self.c_type,
            'obj_id': self.other_gallery.pk,
            'field': 'logo',
        }
        self.is_not_callable(
            ajax=True, post=True, kwargs=new_kwargs,
            user=self.gallery.user_connection,
            msg=('Should only be callable, if the current user owns the'
                 ' chosen vendor.'))


class AJAXImageCropViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``AJAXImageCropView`` generic view class."""
    view_class = views.AJAXImageCropView

    def setUp(self):
        self.image = mixer.blend('user_media.UserMediaImage')
        self.image2 = mixer.blend('user_media.UserMediaImage')

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
        self.is_not_callable(user=self.image.user)
        data = {'x': 10, 'x2': 15, 'y': 2, 'y2': 10, 'w': 5, 'h': 8}
        self.is_postable(user=self.image.user, data=data, ajax=True)
        self.is_not_callable(user=self.image2.user, ajax=True, post=True)
