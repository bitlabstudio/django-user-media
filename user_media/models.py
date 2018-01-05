"""Models for the ``django-user-media`` app."""
import glob
import os
import uuid

from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


def get_image_file_path(instance, filename):
    """Returns a unique filename for images."""
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4(), ext)
    return os.path.join(
        'user_media', str(instance.user.pk), 'images', filename)


class UserMediaImage(models.Model):
    """
    An image that can be uploaded by a user.

    If the image belongs to a certain object that is owned by the user, it
    can be tied to that object using the generic foreign key. That object
    must have a foreign key to ``auth.User`` (or another user model) and that
    field must be called ``user``.

    :user: The user this image belongs to.
    :content_type: If this image belongs to a certain object (i.e. a Vehicle),
      this should be the object's ContentType.
    :object_id: If this image belongs to a certain object (i.e. a Vehicle),
      this should be the object's ID.
    :image: The uploaded image.
    :position: The position of the image in case of multiple ones.
    :thumb_x: Thumbnail starting point on the x-axis.
    :thumb_x2: Thumbnail ending point on the x-axis.
    :thumb_y: Thumbnail starting point on the y-axis.
    :thumb_y2: Thumbnail ending point on the y-axis.
    :thumb_w: Thumbnail width.
    :thumb_h: Thumbnail height.

    """
    user = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True,
        on_delete=models.CASCADE,
    )

    object_id = models.PositiveIntegerField(
        null=True, blank=True
    )

    content_object = fields.GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(
        upload_to=get_image_file_path,
        null=True, blank=True,
        verbose_name=_('Image'),
    )

    generic_position = fields.GenericRelation(
        'generic_positions.ObjectPosition'
    )

    thumb_x = models.PositiveIntegerField(
        verbose_name=_('Thumbnail x'),
        null=True, blank=True,
    )

    thumb_x2 = models.PositiveIntegerField(
        verbose_name=_('Thumbnail x2'),
        null=True, blank=True,
    )

    thumb_y = models.PositiveIntegerField(
        verbose_name=_('Thumbnail y'),
        null=True, blank=True,
    )

    thumb_y2 = models.PositiveIntegerField(
        verbose_name=_('Thumbnail y2'),
        null=True, blank=True,
    )

    thumb_w = models.PositiveIntegerField(
        verbose_name=_('Thumbnail width'),
        null=True, blank=True,
    )

    thumb_h = models.PositiveIntegerField(
        verbose_name=_('Thumbnail height'),
        null=True, blank=True,
    )

    @property
    def box_coordinates(self):
        """Returns a thumbnail's coordinates."""
        if (
            self.thumb_x is not None and
            self.thumb_y is not None and
            self.thumb_x2 is not None and
            self.thumb_y2 is not None
        ):
            return (
                int(self.thumb_x),
                int(self.thumb_y),
                int(self.thumb_x2),
                int(self.thumb_y2),
            )
        return False

    def large_size(self, as_string=True):
        """Returns a thumbnail's large size."""
        size = getattr(settings, 'USER_MEDIA_THUMB_SIZE_LARGE', (150, 150))
        if as_string:
            return u'{}x{}'.format(size[0], size[1])
        return size

    def small_size(self, as_string=True):
        """Returns a thumbnail's small size."""
        size = getattr(settings, 'USER_MEDIA_THUMB_SIZE_SMALL', (95, 95))
        if as_string:
            return u'{}x{}'.format(size[0], size[1])
        return size


@receiver(post_delete, sender=UserMediaImage)
def image_post_delete_handler(sender, instance, **kwargs):
    """
    Makes sure that a an image is also deleted from the media directory.

    This should prevent a load of "dead" image files on disc.

    """
    for f in glob.glob('{}/{}*'.format(instance.image.storage.location,
                                       instance.image.name)):
        if not os.path.isdir(f):
            instance.image.storage.delete(f)
