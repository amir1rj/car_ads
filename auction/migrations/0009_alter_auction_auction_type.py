# Generated by Django 4.2.10 on 2024-05-17 15:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auction", "0008_alter_auction_auction_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auction",
            name="auction_type",
            field=models.CharField(
                choices=[("متفرقه", "متفرقه"), ("ملک", "ملک"), ("ماشین", "ماشین")],
                default="ماشین",
                max_length=255,
                verbose_name="نوع مزایده",
            ),
        ),
    ]
