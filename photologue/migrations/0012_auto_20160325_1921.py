# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-25 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0011_photo_aardvark'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photo',
            options={'get_latest_by': 'date_added', 'ordering': ['species'], 'verbose_name': 'snake', 'verbose_name_plural': 'snakes'},
        ),
        migrations.RemoveField(
            model_name='photo',
            name='aardvark',
        ),
        migrations.AddField(
            model_name='photo',
            name='authority',
            field=models.TextField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='photo',
            name='source',
            field=models.URLField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='photo',
            name='species',
            field=models.TextField(blank=True, max_length=100),
        ),
    ]
