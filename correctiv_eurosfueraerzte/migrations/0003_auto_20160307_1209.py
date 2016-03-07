# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0002_auto_20160229_1707'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='drug',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='observationalstudy',
            options={'ordering': ('-start_date',)},
        ),
        migrations.AlterModelOptions(
            name='pharmacompany',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='observationalstudy',
            name='reference',
            field=models.CharField(max_length=1024, blank=True),
        ),
    ]
