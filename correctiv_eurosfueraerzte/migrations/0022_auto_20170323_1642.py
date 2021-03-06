# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-23 15:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0021_paymentrecipient_aggs'),
    ]

    operations = [
        migrations.AddField(
            model_name='zerodoctor',
            name='address_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='zerodoctor',
            name='specialisation',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='zerodoctor',
            name='web',
            field=models.URLField(blank=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name='paymentrecipient',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=dict),
        ),
    ]
