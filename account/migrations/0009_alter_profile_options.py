# Generated by Django 5.0.1 on 2024-02-04 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_alter_profile_gender_alter_user_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Profile', 'verbose_name_plural': 'Profiles'},
        ),
    ]
