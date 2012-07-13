"""Factories for the ``django-user-media`` app."""
from django_libs.tests.factories import UserFactory
import factory

from user_media.models import UserMediaImage
from user_media.tests.test_app.models import DummyModel


class DummyModelFactory(factory.Factory):
    FACTORY_FOR = DummyModel
    user = factory.SubFactory(UserFactory)


class UserMediaImageFactory(factory.Factory):
    """Factory for ``UserMediaImage`` objects."""
    FACTORY_FOR = UserMediaImage

    user = factory.SubFactory(UserFactory)
