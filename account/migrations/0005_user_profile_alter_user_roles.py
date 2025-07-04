# Generated by Django 5.0.1 on 2024-01-27 00:17

import account.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_pendinguser_alter_user_options_user_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='roles',
            field=models.CharField(blank=True, choices=[('EXHIBITOR', 'EXHIBITOR'), ('CUSTOMER', 'CUSTOMER')], default=account.utils.default_role, max_length=20),
        ),
    ]
