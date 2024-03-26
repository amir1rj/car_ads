from django.db import models
from account.models import User
from account.utils import PROVINCES
from ads.constants import *
from django.core.exceptions import ValidationError


class Exhibition(models.Model):
    """
    مدل مربوط به اطلاعات غرفه داران
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر")

    # اطلاعات پایه ای
    company_name = models.CharField(max_length=255, unique=True, verbose_name="نام شرکت")
    contact_name = models.CharField(max_length=100, blank=True, verbose_name="نام نماینده ")
    contact_phone = models.CharField(max_length=100, blank=True, verbose_name="تلفن تماس")

    # موقعیت مکانی (اختیاری)
    city = models.CharField(
        max_length=30, choices=PROVINCES, verbose_name="شهر", blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, verbose_name="آدرس")

    # اطلاعات توصیفی
    description = models.TextField(blank=True, verbose_name="توضیحات")

    social_media_links = models.TextField(blank=True, default=dict, verbose_name="لینک‌های شبکه‌های اجتماعی")
    logo = models.ImageField(upload_to='exhibition_logos', blank=True, verbose_name="لوگو", null=True, )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "نمایشگاه"
        verbose_name_plural = " نمایشگاه ها"


class ExhibitionVideo(models.Model):
    """
    مدل مربوط به ویدیوهای آپلود شده توسط غرفه داران
    """
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, verbose_name="غرفه دار", related_name="videos")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    video_file = models.FileField(upload_to='exhibition_videos',
                                  verbose_name="فایل ویدیو", null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ آپلود")

    def __str__(self):
        return self.title


class ExhView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exh = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'exh')


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name="برند")
    logo = models.ImageField(upload_to="brand/logos", null=True, blank=True, verbose_name="لوگو")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="مدل خودرو")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="models", verbose_name="برند")

    class Meta:
        verbose_name = "مدل"
        verbose_name_plural = "مدل‌ها"

    def __str__(self):
        return self.title


# مدل مربوط به آگهی خودرو


class Car(models.Model):
    """
    مدل مربوط به آگهی خودرو
    """
    # general information of ads
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="فروشنده", related_name="cars")
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, verbose_name="نمایشگاه", related_name="cars",
                                   null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات")
    price = models.PositiveIntegerField(verbose_name="قیمت")
    is_negotiable = models.BooleanField(default=True, verbose_name="قابل مذاکره")
    city = models.CharField(
        max_length=30, choices=PROVINCES, verbose_name="شهر", blank=True, null=True)

    # general information of car
    car_type = models.CharField(max_length=255, choices=CAR_TYPE_CHOICES, verbose_name="نوع خودرو")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="برند", blank=True, null=True)
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name="مدل خودرو", null=True, blank=True)
    # optional
    promoted_model = models.CharField(max_length=255, verbose_name="مدل پیشنهادی ", null=True, blank=True)

    year = models.PositiveIntegerField(verbose_name="سال ساخت")
    kilometer = models.PositiveIntegerField(verbose_name="کارکرد کیلومتر")
    body_type = models.CharField(max_length=255, choices=BODY_TYPE_CHOICES, verbose_name="نوع بدنه", null=True,
                                 blank=True)
    color = models.CharField(max_length=255, verbose_name="رنگ", null=True, blank=True)
    color_description = models.TextField(blank=True, null=True, verbose_name="جزعیات رنگ شدگی")
    fuel_type = models.CharField(max_length=255, choices=FUEL_TYPE_CHOICES, verbose_name="نوع سوخت")
    # Passenger Cars optional
    transmission = models.CharField(max_length=255, choices=TRANSMISSION_CHOICES, verbose_name="نوع گیربکس", null=True,
                                    blank=True)
    body_condition = models.CharField(
        max_length=255,
        choices=BODY_CONDITION_CHOICES,
        null=True,
        blank=True,
        verbose_name="وضعیت بدنه خودرو",
    )
    chassis_condition = models.CharField(
        max_length=255, choices=CHASSIS_CONDITION_CHOICES, default=("سالم", "سالم"), verbose_name="وضعیت شاسی",
        null=True, blank=True
    )
    # Heavyweights optional
    weight = models.IntegerField(verbose_name="وزن ماشین", null=True, blank=True)
    payload_capacity = models.IntegerField(verbose_name="حداکثر وزن ناخالص مجاز وسیله نقلیه", null=True, blank=True)
    wheel_number = models.SmallIntegerField(verbose_name="تعداد چرخ" , default=4)
    # contact information
    phone_numbers = models.CharField(max_length=12, verbose_name="شماره تلفن")
    address = models.CharField(max_length=255, verbose_name="آدرس")
    # ads status
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    is_promoted = models.BooleanField(default=False, verbose_name="پیشنهادی")
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        if self.brand and self.model:
            return f" ({self.brand} {self.model}) "
        else:
            return f"{self.promoted_model}  "

    class Meta:
        ordering = ["-is_promoted", "-created_at"]
        verbose_name = "خودرو"
        verbose_name_plural = "خودروها"
        get_latest_by = "created_at"

    def save(self, *args, **kwargs):
        if self.body_condition == 'رنگ شدگی' and not self.color_description:
            raise ValidationError("اگر وضعیت بدنه خودرو رنگ شدگی است، توضیحات رنگ الزامی است.")
        if self.exhibition and not (self.user.roles == "EXHIBITOR"):
            raise ValidationError("this car could not have exhibition")
        if ((self.model is None) or (self.brand is None)) and self.promoted_model is None:
            raise ValidationError("you must fill brand and model or promoted model")
        if not self.user.roles == "EXHIBITOR":
            if self.user.cars.filter(status="active").count() > 3:
                raise ValidationError("you can not have more than 3 cars")
        if self.car_type == 'ماشین‌آلات سنگین' and not (self.weight or self.payload_capacity or self.wheel_number):
            raise ValidationError("you must fill weight, payload_capacity and wheel_number")
        return super().save(*args, **kwargs)

    def clean(self):
        if (self.body_condition == 'رنگ شدگی') and not self.color_description:
            raise ValidationError("اگر وضعیت بدنه خودرو رنگ شدگی است، توضیحات رنگ الزامی است.")
        if (self.exhibition) and not (self.user.roles == "EXHIBITOR"):
            raise ValidationError("this car could not have exhibition")
        if ((self.model is None) or (self.brand is None)) and self.promoted_model is None:
            raise ValidationError("you must fill brand and model or promoted model")
        if self.car_type == 'ماشین‌آلات سنگین' and not (self.weight or self.payload_capacity or self.wheel_number):
            raise ValidationError("you must fill weight, payload_capacity and wheel_number")
        return super().clean()


class Image(models.Model):
    ad = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images", null=True, blank=True,
                           verbose_name="آگهی")
    image = models.ImageField(upload_to="ads")

    class Meta:
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"


class Feature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="features",
                            verbose_name="خودرو")
    name = models.CharField(max_length=255, verbose_name="امکانات")

    class Meta:
        verbose_name = "امکانات"
        verbose_name_plural = "امکانات"

    def __str__(self):
        return self.name


class View(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.ForeignKey(Car, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')
