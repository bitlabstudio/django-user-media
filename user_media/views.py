"""Views for the ``django-user-media`` app."""
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView

from user_media.forms import UserMediaImageForm
from user_media.models import UserMediaImage


class CreateImageView(CreateView):
    model = UserMediaImage
    form_class = UserMediaImageForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.next = request.POST.get('next', '') or request.GET.get('next', '')
        self.user = request.user
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
                self.content_object = self.content_type.get_object_for_this_type(
                    pk=self.object_id)
            except ObjectDoesNotExist:
                raise Http404

        if self.content_object:
            # Check if the user forged the URL and tries to append the image to
            # an object that does not belong to him
            if not self.content_object.user == self.user:
                raise Http404

        return super(CreateImageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CreateImageView, self).get_context_data(**kwargs)
        ctx.update({
            'next': self.next,
        })
        return ctx

    def get_form_kwargs(self, **kwargs):
        kwargs = super(CreateImageView, self).get_form_kwargs()
        kwargs.update({
            'user': self.user,
            'content_type': self.content_type,
            'object_id': self.object_id,
        })
        return kwargs

    def get_success_url(self):
        if self.next:
            return self.next
        if self.content_object:
            return self.content_object.get_absolute_url()
        raise Exception(
            'No content object given. Please provide ``next`` in your POST'
            ' data')


class DeleteImageView(DeleteView):
    model = UserMediaImage

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.next = request.POST.get('next', '') or request.GET.get('next', '')
        self.user = request.user
        return super(DeleteImageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DeleteImageView, self).get_context_data(**kwargs)
        ctx.update({
            'next': self.next or self.object.content_object.get_absolute_url(),
        })
        return ctx

    def get_queryset(self):
        queryset = super(DeleteImageView, self).get_queryset()
        queryset = queryset.filter(user=self.user)
        return queryset

    def get_success_url(self):
        if self.next:
            return self.next
        if self.object.content_object:
            return self.object.content_object.get_absolute_url()
        raise Exception(
            'No content object given. Please provide ``next`` in your POST'
            ' data')
