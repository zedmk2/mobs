# Generated by Django 2.0.2 on 2018-07-01 00:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0006_property_rl_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(max_length=20)),
                ('route_num', models.IntegerField()),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='route_driver', to='work.Employee')),
                ('route_location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='route_location', to='work.Property')),
            ],
            options={
                'verbose_name_plural': 'routes',
                'ordering': ['weekday'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together={('weekday', 'route_num')},
        ),
    ]