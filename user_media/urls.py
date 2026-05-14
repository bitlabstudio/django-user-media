"""URLs for the ``django-user-media`` app."""

from django.urls import re_path

from .views import (
    AJAXImageCropView,
    AJAXMultipleImageUploadView,
    AJAXSingleImageUploadView,
    CreateImageView,
    DeleteImageView,
    UpdateImageView,
)


urlpatterns = [
    re_path(
        r"^image/create/$",
        CreateImageView.as_view(),
        name="user_media_image_create_no_ctype",
    ),
    re_path(
        r"^image/(?P<content_type>[-\w]+)/(?P<object_id>\d+)/create/$",
        CreateImageView.as_view(),
        name="user_media_image_create",
    ),
    re_path(
        r"^image/(?P<pk>\d+)/$", UpdateImageView.as_view(), name="user_media_image_edit"
    ),
    re_path(
        r"^image/(?P<pk>\d+)/crop/$",
        AJAXImageCropView.as_view(),
        name="user_media_image_crop",
    ),
    re_path(
        r"^image/(?P<pk>\d+)/delete/$",
        DeleteImageView.as_view(),
        name="user_media_image_delete",
    ),
    re_path(
        r"^upload-single/(?P<c_type>[-\w]+)/(?P<obj_id>\d+)/(?P<field>\w+)/$",
        AJAXSingleImageUploadView.as_view(),
        name="user_media_ajax_single_upload",
    ),
    re_path(
        r"^upload-multiple/(?P<c_type>[-\w]+)/(?P<obj_id>\d+)/$",
        AJAXMultipleImageUploadView.as_view(),
        name="user_media_ajax_multiple_upload",
    ),
]
