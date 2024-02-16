from django.db import models
from account.models import User
from ads.constants import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name="برند")

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
    # اطلاعات کلی
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="فروشنده", related_name="cars")
    description = models.TextField(verbose_name="توضیحات")
    price = models.PositiveIntegerField(verbose_name="قیمت")
    is_negotiable = models.BooleanField(default=True, verbose_name="قابل مذاکره")

    # اطلاعات خودرو
    car_type = models.CharField(max_length=255, choices=CAR_TYPE_CHOICES, verbose_name="نوع خودرو")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="برند")
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name="مدل خودرو")
    year = models.PositiveIntegerField(verbose_name="سال ساخت")
    kilometer = models.PositiveIntegerField(verbose_name="کارکرد کیلومتر")
    body_type = models.CharField(max_length=255, choices=BODY_TYPE_CHOICES, verbose_name="نوع بدنه")
    color = models.CharField(max_length=255, verbose_name="رنگ")
    color_description = models.TextField(blank=True, null=True,verbose_name="جزعیات رنگ شدگی")
    transmission = models.CharField(max_length=255, choices=TRANSMISSION_CHOICES, verbose_name="نوع گیربکس")
    fuel_type = models.CharField(max_length=255, choices=FUEL_TYPE_CHOICES, verbose_name="نوع سوخت")
    body_condition = models.CharField(
        max_length=255,
        choices=BODY_CONDITION_CHOICES,
        null=True,
        blank=True,
        verbose_name="وضعیت بدنه خودرو",
    )
    chassis_condition = models.CharField(
        max_length=255, choices=CHASSIS_CONDITION_CHOICES, default=("سالم", "سالم"), verbose_name="وضعیت شاسی"
    )


    # اطلاعات تماس
    phone_numbers = models.CharField(max_length=12, verbose_name="شماره تلفن")
    address = models.CharField(max_length=255, verbose_name="آدرس")

    # وضعیت آگهی
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    is_promoted = models.BooleanField(default=False, verbose_name="پیشنهادی")

    def __str__(self):
        return f" ({self.brand} {self.model}) {self.description[:20]}"

    class Meta:
        ordering = ["-is_promoted", "-created_at"]
        verbose_name = "خودرو"
        verbose_name_plural = "خودروها"
        get_latest_by = "created_at"

    def clean_color_description(self):
        if self.body_condition == 'رنگ شدگی' and not self.color_description:
            raise ValidationError("اگر وضعیت بدنه خودرو رنگ شدگی است، توضیحات رنگ الزامی است.")
        return self.color_description


class Image(models.Model):
    ad = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images", null=True, blank=True,
                           verbose_name="آگهی")
    image = models.ImageField(upload_to="ads")

    class Meta:
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"


class Feature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="features",
                            verbose_name="خودرو")  # Add this line
    name = models.CharField(max_length=255, verbose_name="امکانات")

    class Meta:
        verbose_name = "امکانات"
        verbose_name_plural = "امکانات"

    def __str__(self):
        return self.name
