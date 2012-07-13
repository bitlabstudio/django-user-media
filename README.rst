Django User Media
=================

Almost all modern web apps allow their users to upload content such as audio,
video or images. This raises a number of issues if that content should not be
visible to the whole world by default.

If you have a UserProfile model and add an ImageField to it, you need to
come up with a good idea on how to save those images. It is probably not a good
idea to keep the original filenames as they might disturb your server's file
system and open doors for hackers, who might try to brute-force against your
``/media/user_profiles/`` in the hope to steal some valuable files.

Since it seems inevitable to implement a function for Django's FileField's
``upload_to`` attribute I thought that this might be a candidate for a reusable
app.

**This project is experimental**. We are using it on two completely different
live projects and will hopefully come up with an implementation that is so
generic that it can safely be used by anyone.

Since we are dealing with files here and not only with a database, backwards
incompatible changes might turn out to be a pain in the ass to deploy on your
production sites. You have been warned.

Installation
------------

To get the latest stable release from PyPi::

    $ pip install django-user-media

To get the latest commit from GitHub::

    $ pip install -e git://github.com/bitmazk/django-user-media.git#egg=user_media

Usage
-----

See the docs folder for descriptions of the different tools this project
provides.

Or read the docs here: http://django-user-media.readthedocs.org/en/latest/

Contribute
----------

If you want to contribute to this project, please perform the following steps::

    # Fork this repository
    # Clone your fork
    $ mkvirtualenv -p python2.7 django-libs
    $ pip install -r requirements.txt

    $ git co -b feature_branch master
    # Implement your feature and tests
    $ git add . && git commit
    $ git push -u origin feature_branch
    # Send us a pull request for your feature branch
