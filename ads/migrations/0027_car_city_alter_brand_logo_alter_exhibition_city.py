# Generated by Django 4.2.10 on 2024-03-08 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0026_alter_exhibition_options_brand_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='city',
            field=models.CharField(blank=True, choices=[('آذربایجان شرقی', 'آذربایجان شرقی'), ('آذربایجان غربی', 'آذربایجان غربی'), ('اصفهان', 'اصفهان'), ('البرز', 'البرز'), ('ایلام', 'ایلام'), ('بوشهر', 'بوشهر'), ('تهران', 'تهران'), ('چهارمحال و بختیاری', 'چهارمحال و بختیاری'), ('خراسان جنوبی', 'خراسان جنوبی'), ('خراسان رضوی', 'خراسان رضوی'), ('خراسان شمالی', 'خراسان شمالی'), ('خوزستان', 'خوزستان'), ('زنجان', 'زنجان'), ('سمنان', 'سمنان'), ('سیستان و بلوچستان', 'سیستان و بلوچستان'), ('فارس', 'فارس'), ('قزوین', 'قزوین'), ('قم', 'قم'), ('کردستان', 'کردستان'), ('کرمان', 'کرمان'), ('کرمانشاه', 'کرمانشاه'), ('کهگیلویه و بویراحمد', 'کهگیلویه و بویراحمد'), ('گلستان', 'گلستان'), ('لرستان', 'لرستان'), ('گیلان', 'گیلان'), ('همدان', 'همدان'), ('یزد', 'یزد')], max_length=30, null=True, verbose_name='شهر'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='brand/logos', verbose_name='لوگو'),
        ),
        migrations.AlterField(
            model_name='exhibition',
            name='city',
            field=models.CharField(blank=True, choices=[('آذربایجان شرقی', 'آذربایجان شرقی'), ('آذربایجان غربی', 'آذربایجان غربی'), ('اصفهان', 'اصفهان'), ('البرز', 'البرز'), ('ایلام', 'ایلام'), ('بوشهر', 'بوشهر'), ('تهران', 'تهران'), ('چهارمحال و بختیاری', 'چهارمحال و بختیاری'), ('خراسان جنوبی', 'خراسان جنوبی'), ('خراسان رضوی', 'خراسان رضوی'), ('خراسان شمالی', 'خراسان شمالی'), ('خوزستان', 'خوزستان'), ('زنجان', 'زنجان'), ('سمنان', 'سمنان'), ('سیستان و بلوچستان', 'سیستان و بلوچستان'), ('فارس', 'فارس'), ('قزوین', 'قزوین'), ('قم', 'قم'), ('کردستان', 'کردستان'), ('کرمان', 'کرمان'), ('کرمانشاه', 'کرمانشاه'), ('کهگیلویه و بویراحمد', 'کهگیلویه و بویراحمد'), ('گلستان', 'گلستان'), ('لرستان', 'لرستان'), ('گیلان', 'گیلان'), ('همدان', 'همدان'), ('یزد', 'یزد')], max_length=30, null=True, verbose_name='شهر'),
        ),
    ]
