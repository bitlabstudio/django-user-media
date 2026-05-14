"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
As you know, every app must be hooked into your main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""

from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog


from .test_app.views import HomeView

admin.autodiscover()

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    re_path(r"^jsi18n.js$", JavaScriptCatalog.as_view(), name="javascript_catalog"),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^positions/", include("generic_positions.urls")),
    re_path(r"^user_media/", include("user_media.urls")),
    re_path(r"^$", HomeView.as_view()),
]
