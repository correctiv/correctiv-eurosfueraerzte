# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import djorm_pgfulltext.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('active_ingredient', models.CharField(max_length=512, blank=True)),
                ('medical_indication', models.CharField(max_length=512, blank=True)),
                ('atc_code', models.CharField(max_length=15, blank=True)),
                ('search_index', djorm_pgfulltext.fields.VectorField()),
            ],
        ),
        migrations.CreateModel(
            name='ObservationalStudy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('drug_title', models.CharField(max_length=1024, blank=True)),
                ('drug_slug', models.SlugField(max_length=1024, blank=True)),
                ('description', models.TextField(blank=True)),
                ('registration_date', models.DateField(null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('company', models.CharField(max_length=1024, blank=True)),
                ('sponsor', models.CharField(max_length=1024, blank=True)),
                ('patient_count', models.IntegerField(null=True, blank=True)),
                ('doc_count', models.IntegerField(null=True, blank=True)),
                ('fee_per_patient', models.DecimalField(null=True, max_digits=19, decimal_places=2, blank=True)),
                ('fee_description', models.TextField(blank=True)),
                ('drugs', models.ManyToManyField(to='correctiv_eurosfueraerzte.Drug')),
            ],
        ),
        migrations.CreateModel(
            name='PharmaCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('web', models.CharField(max_length=1024, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='drug',
            name='pharma_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='correctiv_eurosfueraerzte.PharmaCompany', null=True),
        ),
    ]
