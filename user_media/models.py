"""Models for the ``django-user-media`` app."""
import os
import uuid

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
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
    must have a foreign key to ``auth.User`` and that field must be called
    ``user``.

    :user: The user this image belongs to.
    :content_type: If this image belongs to a certain object (i.e. a Vehicle),
      this should be the object's ContentType.
    :object_id: If this image belongs to a certain object (i.e. a Vehicle),
      this should be the object's ID.
    :image: The uploaded image.

    """
    user = models.ForeignKey(
        'auth.User',
        verbose_name=_('User'),
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True, blank=True,
    )

    object_id = models.PositiveIntegerField(
        null=True, blank=True
    )

    content_object = generic.GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(
        upload_to=get_image_file_path,
        null=True, blank=True,
        verbose_name=_('Image'),
    )
