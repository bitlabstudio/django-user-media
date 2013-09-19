"""Views for the ``test_app`` app."""
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView

from .models import DummyGallery


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self):
        context = super(HomeView, self).get_context_data()
        try:
            context.update({
                'dummy_gallery': DummyGallery.objects.all()[0],
                'gallery_ctype': ContentType.objects.get_for_model(
                    DummyGallery.objects.all()[0]).model,
            })
        except IndexError:
            pass
        return context
