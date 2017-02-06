# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('correctiv_eurosfueraerzte', '0003_auto_20160307_1209'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='drug',
            options={'ordering': ('name',), 'verbose_name': 'Drugs', 'verbose_name_plural': 'Drugs'},
        ),
        migrations.AlterModelOptions(
            name='observationalstudy',
            options={'ordering': ('-start_date',), 'verbose_name': 'observational study', 'verbose_name_plural': 'observational studies'},
        ),
        migrations.AlterModelOptions(
            name='pharmacompany',
            options={'ordering': ('name',), 'verbose_name': 'Pharma Company', 'verbose_name_plural': 'Pharma Companies'},
        ),
        migrations.AddField(
            model_name='pharmacompany',
            name='search_index',
            field=models.CharField(max_length=512, blank=True),
        ),
        migrations.AlterField(
            model_name='drug',
            name='active_ingredient',
            field=models.CharField(max_length=512, verbose_name='active ingredient', blank=True),
        ),
        migrations.AlterField(
            model_name='drug',
            name='medical_indication',
            field=models.CharField(max_length=512, verbose_name='medical indication', blank=True),
        ),
        migrations.AlterField(
            model_name='drug',
            name='pharma_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='pharma company', blank=True, to='correctiv_eurosfueraerzte.PharmaCompany', null=True),
        ),
        migrations.AlterField(
            model_name='observationalstudy',
            name='company',
            field=models.CharField(max_length=1024, verbose_name='executing company', blank=True),
        ),
        migrations.AlterField(
            model_name='observationalstudy',
            name='drugs',
            field=models.ManyToManyField(to='correctiv_eurosfueraerzte.Drug', verbose_name='drugs'),
        ),
        migrations.AlterField(
            model_name='observationalstudy',
            name='sponsor',
            field=models.CharField(max_length=1024, verbose_name='sponsor', blank=True),
        ),
    ]
