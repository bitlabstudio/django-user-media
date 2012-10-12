"""Views for the ``django-user-media`` app."""
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView

from user_media.forms import UserMediaImageForm
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


class CreateImageView(UserMediaImageViewMixin, CreateView):
    form_class = UserMediaImageForm

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

        if self.content_object:
            # Check if the user forged the URL and tries to append the image to
            # an object that does not belong to him
            if not self.content_object.user == self.user:
                raise Http404

        return super(CreateImageView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UserMediaImageViewMixin, self).get_form_kwargs()
        kwargs.update({
            'user': self.user,
            'content_type': self.content_type,
            'object_id': self.object_id,
        })
        return kwargs


class DeleteImageView(UserMediaImageViewMixin, DeleteView):
    """Deletes an `UserMediaImage` object."""
    model = UserMediaImage

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Adds useful objects to the class.

        """
        self._add_next_and_user(request)
        return super(DeleteImageView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Making sure that a user can only delete his own images.

        Even when he forges the request URL.

        """
        queryset = super(DeleteImageView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset
