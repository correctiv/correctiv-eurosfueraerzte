# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-03 19:15
from __future__ import unicode_literals

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0015_observationalstudy_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drug',
            name='search_index',
        ),
        migrations.RemoveField(
            model_name='paymentrecipient',
            name='search_index',
        ),
        migrations.RemoveField(
            model_name='pharmacompany',
            name='search_index',
        ),
        migrations.AddField(
            model_name='drug',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(default=b''),
        ),
        migrations.AddField(
            model_name='paymentrecipient',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(default=b''),
        ),
        migrations.AddField(
            model_name='pharmacompany',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(default=b''),
        ),
    ]
