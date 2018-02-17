# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-17 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audition_management', '0002_auto_20180213_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='status',
            field=models.IntegerField(choices=[(0, 'Closed'), (1, 'Open')], default=1, verbose_name='Status'),
        ),
    ]
