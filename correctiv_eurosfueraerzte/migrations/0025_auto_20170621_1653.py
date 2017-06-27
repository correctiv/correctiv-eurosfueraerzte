# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-21 14:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0024_auto_20170526_1123'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX correctiv_eurosfueraerzte_paymentrecipient_search_vector_idx ON public.correctiv_eurosfueraerzte_paymentrecipient USING gin (search_vector); ",
            "DROP INDEX public.correctiv_eurosfueraerzte_paymentrecipient_search_vector_idx;"
        )
    ]