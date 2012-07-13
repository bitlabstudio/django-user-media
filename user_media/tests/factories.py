"""Factories for the ``django-user-media`` app."""
from django_libs.tests.factories import UserFactory
import factory

from user_media.models import UserMediaImage


class UserMediaImageFactory(factory.Factory):
    """Factory for ``UserMediaImage`` objects."""
    FACTORY_FOR = UserMediaImage

    user = factory.SubFactory(UserFactory)
