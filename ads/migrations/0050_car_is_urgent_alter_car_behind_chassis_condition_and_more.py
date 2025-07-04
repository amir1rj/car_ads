# Generated by Django 4.2.10 on 2024-10-02 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0049_remove_car_car_type_remove_car_chassis_condition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='is_urgent',
            field=models.BooleanField(default=False, verbose_name='فوری'),
        ),
        migrations.AlterField(
            model_name='car',
            name='behind_chassis_condition',
            field=models.CharField(blank=True, choices=[('ضربه خورده', 'ضربه خورده'), ('سالم', 'سالم'), ('رنگ شده', 'رنگ شده')], default=('سالم', 'سالم'), max_length=255, null=True, verbose_name='وضعیت شاسی عقب'),
        ),
        migrations.AlterField(
            model_name='car',
            name='front_chassis_condition',
            field=models.CharField(blank=True, choices=[('ضربه خورده', 'ضربه خورده'), ('سالم', 'سالم'), ('رنگ شده', 'رنگ شده')], default=('سالم', 'سالم'), max_length=255, null=True, verbose_name='وضعیت شاسی جلو'),
        ),
        migrations.AlterField(
            model_name='carmodel',
            name='car_type',
            field=models.CharField(choices=[('سدان', 'سدان'), ('هاچ\u200cبک', 'هاچ\u200cبک'), ('کراس\u200cاوور', 'کراس\u200cاوور'), ('SUV', 'SUV'), (' وانت', 'وانت'), ('کامیون', 'کامیون'), ('تجهیزات', 'تجهیزات')], max_length=255, verbose_name='نوع خودرو'),
        ),
    ]
