# Generated by Django 5.0.1 on 2024-02-04 20:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_remove_car_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='ad',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_images', to='ads.car'),
        ),
    ]
