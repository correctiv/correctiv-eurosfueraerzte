# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 15:06
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0018_auto_20170317_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='zerodoctor',
            name='geo',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326, verbose_name='Geographic location'),
        ),
    ]
