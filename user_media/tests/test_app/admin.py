"""Admin classes for the ``test_app`` app."""
from django.contrib import admin

from .models import DummyGallery


admin.site.register(DummyGallery)
