# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-25 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0010_auto_20160105_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='aardvark',
            field=models.TextField(default='my aardvark', verbose_name='aardvark'),
        ),
    ]
