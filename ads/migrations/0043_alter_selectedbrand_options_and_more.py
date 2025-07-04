# Generated by Django 4.2.10 on 2024-07-13 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0042_alter_car_body_type_selectedbrand'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='selectedbrand',
            options={'verbose_name': 'برند منتخب', 'verbose_name_plural': 'برندهای منتخب'},
        ),
        migrations.RemoveField(
            model_name='selectedbrand',
            name='brand',
        ),
        migrations.AddField(
            model_name='selectedbrand',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_brand', to='ads.brand', verbose_name='برند منتخب'),
        ),
    ]
