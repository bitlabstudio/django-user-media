# Generated by Django 2.2.28 on 2022-05-05 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_media', '0002_auto_20180105_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermediaimage',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
