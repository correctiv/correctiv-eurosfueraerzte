# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drug',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
        migrations.AlterField(
            model_name='pharmacompany',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
    ]
