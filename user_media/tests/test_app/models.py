"""
Dummy models needed for the tests of the `django-user-media` application.

"""
from django.contrib.contenttypes import generic
from django.db import models


class DummyModel(models.Model):
    """
    Dummy model for tests of the `django-user-media` application.

    Since `UserMediaImage` objects can belong to a content object, we need this
    DummyModel in order to have objects to which a `UserMediaImage` can belong
    to.

    Note the `images` generic relation. It is useful to implement this on your
    content object in order to have easier access to the images that have been
    tied to this content object.

    """
    user = models.ForeignKey('auth.User')

    images = generic.GenericRelation(
        'user_media.UserMediaImage',
    )

    def get_absolute_url(self):
        return '/?foo=bar'

    @property
    def image(self):
        """
        Provides easier access to the image of this content object.

        The generic relation `images` makes it easy to access all images of
        this content object but usually your object is only supposed to have
        one single image. Therefore this property makes it easier to access
        that image.

        """
        try:
            return self.images.all()[0]
        except IndexError:
            return None
