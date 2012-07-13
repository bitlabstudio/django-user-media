"""
This ``urls.py`` is only used when running the tests via ``runtests.py``.
As you know, every app must be hooked into your main ``urls.py`` so that
you can actually reach the app's views (provided it has any views, of course).

"""
from django.conf.urls.defaults import include, patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^$',
        TemplateView.as_view(template_name='home.html'),
    ),

    url(r'^user_media/', include('user_media.urls')),
)
