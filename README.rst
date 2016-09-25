Django User Media
=================

Almost all modern web apps allow their users to upload content such as audio,
video or images. This raises a number of issues if that content should not be
visible to the whole world by default.

If you add an ImageField to your user model, you need to come up with a good
idea on how to save those images. It is probably not a good idea to keep the
original filenames as they might disturb your server's file system and open
doors for hackers, who might try to brute-force against your
``/media/user_profiles/`` in the hope to steal some valuable files.

Since it seems inevitable to implement a function for Django's FileField's
``upload_to`` attribute I thought that this might be a candidate for a reusable
app.


Prerequisites
-------------

You need at least the following packages in your virtualenv:

* Django
* django-libs
* easy_thumbnails
* django-generic-positions
* simplejson


Installation
------------

To get the latest stable release from PyPi::

    $ pip install django-user-media

To get the latest commit from GitHub::

    $ pip install -e git://github.com/bitmazk/django-user-media.git#egg=user_media

Add the app to your ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'user_media',
        'easy_thumbnails',
        'django_libs',
        'generic_positions',

    ]

Hook the app into your main ``urls.py``::

    urlpatterns += patterns('',
        ...
        url(r'^umedia/', include('user_media.urls')),
    )

Run the migrations to create the app's database tables::

    $ ./manage.py migrate user_media


Usage
-----


Add generic relation
++++++++++++++++++++

Let's assume that you have a ``UserProfile`` model and you want to add an
``avatar`` field to that model.

First you might want to add a [``GenericRelation``](https://docs.djangoproject.com/en/1.8/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericRelation) to your ``UserProfile``
model::

    from django.contrib.contenttypes import fields


    class UserProfile(models.Model):
        ...
        user = models.ForeignKey(
            getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        )

        avatar = fields.GenericRelation(
            'user_media.UserMediaImage',
        )


Add property
++++++++++++

Now you will be able to get all uploaded images that belong to a
``UserProfile`` by doing this::

    profile = UserProfile.objects.get(pk=1)
    images = profile.avatar.all()

It makes sense to add a convenience method to your ``UserProfile`` model::

    class UserProfile(models.Model):
        ...
        @property
        def avatar(self):
            try:
                return self.avatar.all()[0]
            except IndexError:
                return None


Add link to update form
+++++++++++++++++++++++

In your templates you can now provide a link to the image creation view like
this (assuming that your ``UserProfile`` object is called ``object`` in the
template's context)::

    <a href="{% url "user_media_image_create" content_type="userprofile" object_id=object.pk %}">Upload your picture</a>

Note that ``userprofile`` is the model name that the ``ContentType`` of your
``UserProfile`` model would return. You can figure this out with ``./manage.py
shell`` for example::

    $ ./manage.py shell
    In [1]: from django.contrib.contenttypes.models import ContentType
    In [2]: from your_app.models import UserProfile
    In [3]: ContentType.objects.get_for_model(UserProfile).model
    Out [1]: u'userprofile'

When visiting that link, the user will see an image upload form. You might
want to override that template (``user_media/usermediaimage_form.html``).

After uploading the image the view should redirect back to the absolute url
of your ``UserProfile``. If you want to redirect to another URL, you can
provide a ``next`` URL parameter via POST or GET::

        <a href="{% url "user_media_image_create" content_type="userprofile" object_id=object.pk %}?next=/foo/bar">Upload your picture</a>


Display images
++++++++++++++

Now you should have all building blocks that you need to add links or buttons
to your templates that call the views of this application. On your
``UserProfile`` detail view you could display the avatar, if available::

    {% if object.avatar %}
        <img src="{{ MEDIA_URL }}{{ object.avatar.image }}" />
    {% endif %}


Delete and edit images
++++++++++++++++++++++

Or in your ``UserProfile`` update view you could display a link to upload a
new image or to delete the existing image::

    {% if form.instance.get_avatar %}
        <p><img src="{{ MEDIA_URL }}{{ form.instance.avatar.image }}" /></p>
        <a href="{% url "user_media_image_delete" pk=form.instance.avatar.pk %}">Delete picture</a>
    {% else %}
        <a href="{% url "user_media_image_create" content_type="userprofile" object_id=form.instance.pk %}">Add profile picture</a>
    {% endif %}

The delete link in this example will render the
``user_media/usermediaimage_confirm_delete.html`` template, which you might
want to override in your project.

A link for editing an existing image would look like this::

        <a href="{% url "user_media_image_edit" pk=form.instance.avatar.pk %}">Edit picture</a>


Upload from your own model form
+++++++++++++++++++++++++++++++

Often you might not want to provide a dedicated form for uploading images but
you might want to have an image field right on the model form of your content
object. In this case you can inherit from `UserMediaImageFormMixin`::

    from django import forms
    from user_media.forms import UserMediaImageFormMixin
    from yourapp.models import UserProfile

    class UserProfileForm(UserMediaImageFormMixin, forms.ModelForm):
        image_label = _('Image')
        require_user_media_image = False
        image_field_name = 'user_media_image'
        image_widget = forms.ClearableFileInput()  # optional

        # your form implementation

The mixin will dynamically add a `forms.ImageField` with the name
`user_media_image` to your form. You can control the label of that field by
setting the `image_label` attribute on your form class. You can also make the
field mandatory by setting the `require_user_media_image` attribute to `True`.

AJAX calls
----------

You might want to call the ``CreateImageView`` from an AJAX call, i.e. when
displaying the form in a jQuery modal. To make life easier the view will
return a different template when the request is an AJAX call.

The names of the alternative templates are
``user_media/partials/ajax_usermediaimage_form.html`` and
``user_media/partials/ajax_usermediaimage_confirm_delete.html``.

Make sure to add a user field to the object::

    user = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        verbose_name=_('User'),
    )

Alternatively you can add a function called ``user_can_edit``: ::

    def user_can_edit(self, user):
        """
        Function, which returns True if the user is allowed edit the instance.

        """
        if user in self.users.all():
            return True
        return False


AJAX multi image upload
-----------------------

If you want to upload multiple images at once, only prepare the following
templates::

    user_media/partials/image_upload.html
    user_media/partials/image.html

Then add styles and jQuery scripts. We've used blueimp's file upload, so you
make it work by adding jQuery & jQuery-UI plus the scripts in::

    user_media/partials/image_upload_scripts.html

Now include the form::

    {% include "user_media/partials/image_upload.html" with object=request.user.get_profile maximum='5' hide_cutout='0' mode="multiple" c_type="profile" %}

You can use the variable `hide_cutout="0"` to hide the link that triggers the
jQuery crop functionality.

You can limit the maximum upload by using the following setting::

    USER_MEDIA_UPLOAD_MAXIMUM = 5


AJAX single image upload
------------------------

You can also combine single and multiple uploads. Just use the templates and
add the wanted variables::

    {% include "user_media/partials/image_upload.html" with object=request.user.get_profile field='logo' mode="single" show_main_thumb="True" %}

Extra classes for newly loaded image
------------------------------------

If you are using the single image upload, your newly uploaded image will
replace the current `img`-element in your `userMediaImageUploaded`-element.
Sometimes you might have special CSS classes on your images and you might want
to add those classes again to the `img` that has just been added to the DOM. In
order to define the classes that should be added to newly loaded image, just
add the `data-img-class="myclass1 myclass2"` attribute to the element that has
the `userMediaImageUploaded` class.

jQuery image cropping
---------------------

You can easily add a frontend image cropping. First of all, add a new thumbnail
processor ``user_media.processors.crop_box``::

    THUMBNAIL_PROCESSORS = (
        'user_media.processors.crop_box',
        ...
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'easy_thumbnails.processors.scale_and_crop',
        'easy_thumbnails.processors.filters',
    )

Then add the cropping template and the relevant js libraries::

    {% include "user_media/partials/crop.html" %}

    <script src="{% static "django_libs/js/getcookie.js" %}"></script>
    <script src="{% static "user_media/js/libs/jquery.Jcrop.js" %}"></script>

You can modify the settings by overwriting the input fields in ``crop.html``.

Check out: http://deepliquid.com/content/Jcrop.html

Now, if a user clicks on ``Select another cutout``, the original image will be
pushed into the crop area, where the user is able to select a frame. If she
then saves the cropped area, the coordinates will be saved to the
``UserMediaImage`` instance.

By using the new thumbnail processor it's easy to use this coordinates to
generate thumbnails::

    {% thumbnail image.image image.small_size box=image.box_coordinates %}


Settings
--------

USER_MEDIA_THUMB_SIZE_SMALL
+++++++++++++++++++++++++++

Default: (95, 95)

Size of the small auto-generated thumbnails, which are processed after
upload/cropping.


USER_MEDIA_THUMB_SIZE_LARGE
+++++++++++++++++++++++++++

Default: (150, 150)

Size of the large auto-generated thumbnails, which are processed after
upload/cropping.


USER_MEDIA_UPLOAD_MAXIMUM
+++++++++++++++++++++++++

Default: 3

Amount of images to be uploaded at a maximum.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-user-media
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch

In order to run the tests, simply execute ``tox``. This will install two new
environments (for Django 1.8 and Django 1.9) and run the tests against both
environments.
