"""URLs for the ``django-user-media`` app."""
from django.conf.urls.defaults import patterns, url

from user_media.views import CreateImageView, DeleteImageView


urlpatterns = patterns('',
    url(r'^image/create/$',
        CreateImageView.as_view(),
        name='user_media_image_create_no_ctype',
    ),

    url(r'^image/(?P<content_type>[-\w]+)/(?P<object_id>\d+)/create/$',
        CreateImageView.as_view(),
        name='user_media_image_create',
    ),

    url(r'^image/(?P<pk>\d+)/delete/$',
        DeleteImageView.as_view(),
        name='user_media_image_delete',
    ),
)
