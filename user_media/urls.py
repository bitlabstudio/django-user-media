"""URLs for the ``django-user-media`` app."""
from django.conf.urls import patterns, url

from user_media.views import (
    AJAXImageCropView,
    AJAXMultipleImageUploadView,
    AJAXSingleImageUploadView,
    CreateImageView,
    DeleteImageView,
    UpdateImageView,
)


urlpatterns = patterns(
    '',
    url(r'^image/create/$',
        CreateImageView.as_view(),
        name='user_media_image_create_no_ctype'),
    url(r'^image/(?P<content_type>[-\w]+)/(?P<object_id>\d+)/create/$',
        CreateImageView.as_view(),
        name='user_media_image_create'),
    url(r'^image/(?P<pk>\d+)/$',
        UpdateImageView.as_view(),
        name='user_media_image_edit'),
    url(r'^image/(?P<pk>\d+)/crop/$',
        AJAXImageCropView.as_view(),
        name='user_media_image_crop'),
    url(r'^image/(?P<pk>\d+)/delete/$',
        DeleteImageView.as_view(),
        name='user_media_image_delete'),
    url(r'^upload-single/(?P<c_type>[-\w]+)/(?P<obj_id>\d+)/(?P<field>\w+)/$',
        AJAXSingleImageUploadView.as_view(),
        name='user_media_ajax_single_upload'),
    url(r'^upload-multiple/(?P<c_type>[-\w]+)/(?P<obj_id>\d+)/$',
        AJAXMultipleImageUploadView.as_view(),
        name='user_media_ajax_multiple_upload'),
)
