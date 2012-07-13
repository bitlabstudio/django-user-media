from django.db import models


class DummyModel(models.Model):
    user = models.ForeignKey('auth.User')

    def get_absolute_url(self):
        return '/?foo=bar'
