# Generated by Django 2.0.2 on 2018-03-12 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0008_property_region'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='region',
            new_name='county',
        ),
    ]
