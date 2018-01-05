"""Views for the ``django-user-media`` app."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, FormView, UpdateView

from django_libs.views_mixins import AjaxResponseMixin
from easy_thumbnails.files import get_thumbnailer
from simplejson import dumps

from user_media.forms import UserMediaImageForm, UserMediaImageSingleUploadForm
from user_media.models import UserMediaImage


class UserMediaImageViewMixin(object):
    """
    Mixin for views that deal with `UserMediaImage` objects.

    When using this mixin please make sure that you call `_add_next_and_user()`
    in your `dispatch()` method.

    """
    model = UserMediaImage

    def _add_next_and_user(self, request):
        self.next = request.POST.get('next', '') or request.GET.get('next', '')
        self.user = request.user

    def get_context_data(self, **kwargs):
        """
        Adds `next` to the context.

        This makes sure that the `next` parameter doesn't get lost if the
        form was submitted invalid.

        """
        ctx = super(UserMediaImageViewMixin, self).get_context_data(**kwargs)
        ctx.update({
            'action': self.action,
            'next': self.next,
        })
        return ctx

    def get_success_url(self):
        """
        Returns the success URL.

        This is either the given `next` URL parameter or the content object's
        `get_absolute_url` method's return value.

        """
        if self.next:
            return self.next
        if self.object and self.object.content_object:
            return self.object.content_object.get_absolute_url()
        raise Exception(
            'No content object given. Please provide ``next`` in your POST'
            ' data')


class CreateImageView(AjaxResponseMixin, UserMediaImageViewMixin, CreateView):
    action = 'create'
    form_class = UserMediaImageForm
    ajax_template_prefix = 'partials/ajax_'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Adds useful objects to the class and performs security checks."""
        self._add_next_and_user(request)
        self.content_object = None
        self.content_type = None
        self.object_id = kwargs.get('object_id', None)

        if kwargs.get('content_type'):
            # Check if the user forged the URL and posted a non existant
            # content type
            try:
                self.content_type = ContentType.objects.get(
                    model=kwargs.get('content_type'))
            except ContentType.DoesNotExist:
                raise Http404

        if self.content_type:
            # Check if the user forged the URL and tries to append the image to
            # an object that does not exist
            try:
                self.content_object = \
                    self.content_type.get_object_for_this_type(
                        pk=self.object_id)
            except ObjectDoesNotExist:
                raise Http404

        if self.content_object and hasattr(self.content_object, 'user'):
            # Check if the user forged the URL and tries to append the image to
            # an object that does not belong to him
            if not self.content_object.user == self.user:
                raise Http404

        return super(CreateImageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CreateImageView, self).get_context_data(**kwargs)
        ctx.update({
            'content_type': self.content_type,
            'object_id': self.object_id,
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(CreateImageView, self).get_form_kwargs()
        kwargs.update({
            'user': self.user,
            'content_type': self.content_type,
            'object_id': self.object_id,
        })
        return kwargs


class DeleteImageView(AjaxResponseMixin, UserMediaImageViewMixin, DeleteView):
    """Deletes an `UserMediaImage` object."""
    action = 'delete'
    model = UserMediaImage
    ajax_template_prefix = 'partials/ajax_'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Adds useful objects to the class."""
        self._add_next_and_user(request)
        return super(DeleteImageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DeleteImageView, self).get_context_data(**kwargs)
        ctx.update({
            'image_pk': self.object.pk,
        })
        return ctx

    def get_queryset(self):
        """
        Making sure that a user can only delete his own images.

        Even when he forges the request URL.

        """
        queryset = super(DeleteImageView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset


class UpdateImageView(AjaxResponseMixin, UserMediaImageViewMixin, UpdateView):
    """Updates an existing `UserMediaImage` object."""
    action = 'update'
    model = UserMediaImage
    form_class = UserMediaImageForm
    ajax_template_prefix = 'partials/ajax_'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Adds useful objects to the class."""
        self._add_next_and_user(request)
        return super(UpdateImageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateImageView, self).get_context_data(**kwargs)
        ctx.update({
            'content_type': self.object.content_type,
            'object_id': self.object.object_id,
            'image_pk': self.object.pk,
        })
        return ctx

    def get_form_kwargs(self):
        kwargs = super(UpdateImageView, self).get_form_kwargs()
        kwargs.update({
            'user': self.user,
            'content_type': self.object.content_type,
            'object_id': self.object.object_id,
        })
        return kwargs

    def get_queryset(self):
        """
        Making sure that a user can only edit his own images.

        Even when he forges the request URL.

        """
        queryset = super(UpdateImageView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset


class AJAXMultipleImageUploadView(CreateView):
    """Ajax view to handle the multiple image upload."""
    model = UserMediaImage
    form_class = UserMediaImageForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.obj_id = kwargs.get('obj_id', None)
        self.user = request.user

        if not request.is_ajax():
            # Since we use a jquery modal and a jquery upload we should only
            # allow ajax calls
            raise Http404

        # Check if the user posted a non existant content type
        try:
            self.c_type = ContentType.objects.get(model=kwargs.get('c_type'))
        except ContentType.DoesNotExist:
            raise Http404

        # Check if the content object exists
        try:
            self.content_object = self.c_type.get_object_for_this_type(
                pk=self.obj_id)
        except ObjectDoesNotExist:
            raise Http404

        # Check for permissions
        # Add a single user to the content object or prepare a user_can_edit
        # function.
        if (not hasattr(self.content_object, 'user') or not
                self.content_object.user == self.user):
            if (not hasattr(self.content_object, 'user_can_edit') or not
                    self.content_object.user_can_edit(self.user)):
                raise Http404
        return super(AJAXMultipleImageUploadView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AJAXMultipleImageUploadView, self).get_form_kwargs()
        # Prepare context for UserMediaImage form
        kwargs.update({
            'user': self.user,
            'content_type': self.c_type,
            'object_id': self.obj_id,
        })
        return kwargs

    def form_valid(self, form):
        # Check if maximum amount of pictures has been reached
        try:
            max_pictures = int(self.request.POST.get('maximum'))
        except (TypeError, ValueError):
            max_pictures = getattr(settings, 'USER_MEDIA_UPLOAD_MAXIMUM', 3)
        stored_images = self.user.usermediaimage_set.filter(
            object_id=self.obj_id, content_type=self.c_type)
        if stored_images.count() >= max_pictures:
            return HttpResponse(_('Maximum amount limit exceeded.'))

        # Save the UserMediaImage
        self.object = form.save()
        f = self.request.FILES.get('image')

        # Generate and get the thumbnail of the uploaded image
        thumbnailer = get_thumbnailer(self.object.image.name)
        thumb = thumbnailer.get_thumbnail({
            'crop': True, 'upscale': True,
            'size': self.object.small_size(as_string=False),
        })

        # Prepare context for the list item html
        context = {
            'image': self.object,
            'mode': 'multiple',
        }
        # Prepare the json response
        data = {'files': [{
            'name': f.name,
            'url': self.object.image.url,
            'thumbnail_url': thumb.url,
            'list_item_html': render_to_string(
                'user_media/partials/image.html', context=context,
                request=self.request),
        }]}
        response = HttpResponse(dumps(data), content_type='application/json')
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class AJAXSingleImageUploadView(FormView):
    """Ajax view to handle the single image upload."""
    form_class = UserMediaImageSingleUploadForm
    template_name = 'user_media/partials/image.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax() or not request.method == 'POST':
            raise Http404
        self.user = request.user
        # Check if the user posted a non existant content type
        try:
            self.c_type = ContentType.objects.get(model=kwargs.get('c_type'))
        except ContentType.DoesNotExist:
            raise Http404

        # Check if the content object exists
        try:
            self.content_object = self.c_type.get_object_for_this_type(
                pk=kwargs.get('obj_id'))
        except ObjectDoesNotExist:
            raise Http404

        # Check if content_object has the requested image field
        if hasattr(self.content_object, kwargs.get('field')):
            self.field_name = kwargs.get('field')
        else:
            raise Http404

        # Check for permissions
        if (not hasattr(self.content_object, 'user') or not
                self.content_object.user == self.user):
            if (not hasattr(self.content_object, 'user_can_edit') or not
                    self.content_object.user_can_edit(self.user)):
                raise Http404
        return super(AJAXSingleImageUploadView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AJAXSingleImageUploadView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.content_object,
            'image_field': self.field_name,
        })
        return kwargs

    def form_valid(self, form):
        # Save the image
        self.content_object = form.save()
        f = self.request.FILES.get(self.field_name)
        image = getattr(self.content_object, self.field_name)
        size = getattr(settings, 'USER_MEDIA_THUMB_SIZE_LARGE', (150, 150))

        # Generate and get the thumbnail of the uploaded image
        thumbnailer = get_thumbnailer(image.name)
        thumb = thumbnailer.get_thumbnail({
            'crop': True, 'upscale': True,
            'size': size,
        })

        # Prepare context for the list item html
        context = {
            'image': image,
            'mode': 'single',
            'size': (self.request.POST.get('size') or
                     u'{}x{}'.format(size[0], size[1])),
        }
        # Prepare the json response
        data = {'files': [{
            'name': f.name,
            'url': image.url,
            'thumbnail_url': thumb.url,
            'list_item_html': render_to_string(
                self.template_name, context=context, request=self.request),
        }]}
        response = HttpResponse(dumps(data), content_type='application/json')
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class AJAXImageCropView(UserMediaImageViewMixin, UpdateView):
    """Ajax view to update an image's crop attributes."""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax() or not request.method == 'POST':
            raise Http404
        self.user = request.user
        self.kwargs = kwargs
        self.object = self.get_object()
        if not self.object.user == self.user:
            raise Http404
        for field in ['x', 'x2', 'y', 'y2', 'w', 'h']:
            # Save the Jcrop values to the image
            setattr(self.object, 'thumb_' + field, request.POST.get(field))
        self.object.save()

        box = (
            int(self.object.thumb_x),
            int(self.object.thumb_y),
            int(self.object.thumb_x2),
            int(self.object.thumb_y2),
        )
        thumbnailer = get_thumbnailer(self.object.image.name)
        thumb = thumbnailer.get_thumbnail({
            'box': box,
            'size': self.object.small_size(as_string=False),
        })
        return HttpResponse(thumb.url)
