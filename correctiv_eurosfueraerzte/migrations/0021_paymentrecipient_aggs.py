# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 20:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0020_paymentrecipient_is_zerodoc'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecipient',
            name='aggs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]