# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-29 03:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0018_match_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statset',
            name='howfarback',
        ),
    ]