# Generated by Django 4.2.10 on 2024-02-26 11:58

import account.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_profile_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pendinguser',
            options={'verbose_name': 'کاربر در انتظار', 'verbose_name_plural': 'کاربران در انتظار'},
        ),
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'پروفایل', 'verbose_name_plural': 'پروفایل\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='token',
            options={'verbose_name': 'توکن', 'verbose_name_plural': 'توکن\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('-created_at',), 'verbose_name': 'کاربر', 'verbose_name_plural': 'کاربران'},
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='password',
            field=models.CharField(max_length=255, null=True, verbose_name='رمز عبور'),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='شماره تلفن'),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='username',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='نام کاربری'),
        ),
        migrations.AlterField(
            model_name='pendinguser',
            name='verification_code',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='کد تأیید'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, choices=[('آذربایجان شرقی', 'آذربایجان شرقی'), ('آذربایجان غربی', 'آذربایجان غربی'), ('اصفهان', 'اصفهان'), ('البرز', 'البرز'), ('ایلام', 'ایلام'), ('بوشهر', 'بوشهر'), ('تهران', 'تهران'), ('چهارمحال و بختیاری', 'چهارمحال و بختیاری'), ('خراسان جنوبی', 'خراسان جنوبی'), ('خراسان رضوی', 'خراسان رضوی'), ('خراسان شمالی', 'خراسان شمالی'), ('خوزستان', 'خوزستان'), ('زنجان', 'زنجان'), ('سمنان', 'سمنان'), ('سیستان و بلوچستان', 'سیستان و بلوچستان'), ('فارس', 'فارس'), ('قزوین', 'قزوین'), ('قم', 'قم'), ('کردستان', 'کردستان'), ('کرمان', 'کرمان'), ('کرمانشاه', 'کرمانشاه'), ('کهگیلویه و بویراحمد', 'کهگیلویه و بویراحمد'), ('گلستان', 'گلستان'), ('لرستان', 'لرستان'), ('گیلان', 'گیلان'), ('همدان', 'همدان'), ('یزد', 'یزد')], max_length=30, null=True, verbose_name='شهر'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True, unique=True, verbose_name='ایمیل'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='نام'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, choices=[('مرد', 'مرد'), ('زن', 'زن')], max_length=3, null=True, verbose_name='جنسیت'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='نام خانوادگی'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(default='images/default.jpeg', upload_to='images/profiles/<django.db.models.fields.related.OneToOneField>/', verbose_name='تصویر پروفایل'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='token',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد'),
        ),
        migrations.AlterField(
            model_name='token',
            name='token',
            field=models.CharField(max_length=8, verbose_name='توکن'),
        ),
        migrations.AlterField(
            model_name='token',
            name='token_type',
            field=models.CharField(choices=[('PASSWORD_RESET', 'PASSWORD_RESET')], max_length=100, verbose_name='نوع توکن'),
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False, verbose_name='مدیر'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='آخرین ورود'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=12, unique=True, verbose_name='شماره تلفن'),
        ),
        migrations.AlterField(
            model_name='user',
            name='roles',
            field=models.CharField(blank=True, choices=[('EXHIBITOR', 'EXHIBITOR'), ('CUSTOMER', 'CUSTOMER')], default=account.utils.default_role, max_length=20, verbose_name='نقش'),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=40, unique=True, verbose_name='نام کاربری'),
        ),
        migrations.AlterField(
            model_name='user',
            name='verified',
            field=models.BooleanField(default=False, verbose_name='تایید شده'),
        ),
    ]
