# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-15 11:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debaserapp', '0004_multiplevarietiesresultsids_consensus_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultsgeneidentifiers',
            name='consensus_html',
            field=models.FileField(default='', upload_to='results-geneids/'),
        ),
    ]