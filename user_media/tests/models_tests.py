"""Tests for the models of the ``django-user-media`` app."""
from django.test import TestCase

from mixer.backend.django import mixer


class UserMediaImageTestCase(TestCase):
    """Tests for the ``UserMediaImage`` model."""
    def setUp(self):
        self.image = mixer.blend('user_media.UserMediaImage')

    def test_box_coordinates(self):
        self.assertFalse(self.image.box_coordinates, msg=(
            'Should return False, if there are no coordinates saved.'))
        self.image.thumb_x = 10
        self.image.thumb_y = 10
        self.image.thumb_x2 = 20
        self.assertFalse(self.image.box_coordinates, msg=(
            'Should return False, if there are not enough coordinates saved.'))
        self.image.thumb_y2 = 20
        self.assertEqual(self.image.box_coordinates, (10, 10, 20, 20), msg=(
            'Should return the coordinates in a tuple.'))

    def test_small_size(self):
        self.assertEqual(self.image.small_size(), '95x95', msg=(
            'Should return a size tuple.'))
        self.assertEqual(self.image.small_size(as_string=False), (95, 95),
                         msg='Should return a size tuple.')

    def test_large_size(self):
        self.assertEqual(self.image.large_size(), '150x150', msg=(
            'Should return a size tuple.'))
        self.assertEqual(self.image.large_size(as_string=False), (150, 150),
                         msg='Should return a size tuple.')
