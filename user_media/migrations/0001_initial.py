# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMediaImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('image', models.ImageField(upload_to='images', null=True, verbose_name='Image', blank=True)),
                ('thumb_x', models.PositiveIntegerField(null=True, verbose_name='Thumbnail x', blank=True)),
                ('thumb_x2', models.PositiveIntegerField(null=True, verbose_name='Thumbnail x2', blank=True)),
                ('thumb_y', models.PositiveIntegerField(null=True, verbose_name='Thumbnail y', blank=True)),
                ('thumb_y2', models.PositiveIntegerField(null=True, verbose_name='Thumbnail y2', blank=True)),
                ('thumb_w', models.PositiveIntegerField(null=True, verbose_name='Thumbnail width', blank=True)),
                ('thumb_h', models.PositiveIntegerField(null=True, verbose_name='Thumbnail height', blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
