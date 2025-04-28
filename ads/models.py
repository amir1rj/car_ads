from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from account.exceptions import CustomValidationError
from account.models import User
from account.utils import PROVINCES
from ads.constants import *


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
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="آدرس")

    # اطلاعات توصیفی
    description = models.TextField(blank=True, verbose_name="توضیحات")
    social_media_links = models.TextField(blank=True, default=dict, verbose_name="لینک‌های شبکه‌های اجتماعی")
    logo = models.ImageField(upload_to='exhibition_logos', blank=True, verbose_name="لوگو", null=True, )

    sells_chinese_cars = models.BooleanField(default=False, verbose_name="فروش ماشین‌های چینی")
    sells_foreign_cars = models.BooleanField(default=False, verbose_name="فروش ماشین‌های خارجی")
    sells_domestic_cars = models.BooleanField(default=False, verbose_name="فروش ماشین‌های داخلی")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    view_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "نمایشگاه"
        verbose_name_plural = " نمایشگاه ها"
        indexes = [
            models.Index(fields=['city'], name="city_index"),
            models.Index(fields=["company_name"], name="Company_name_index")
        ]


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
    type = models.CharField(max_length=255, choices=BRAND_TYPE_CHOICES, verbose_name="نوع خودرو")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="مدل خودرو")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="models", verbose_name="برند")
    car_type = models.CharField(max_length=255, choices=BODY_TYPE_CHOICES, verbose_name="نوع خودرو")

    class Meta:
        verbose_name = "مدل"
        verbose_name_plural = "مدل‌ها"

    def __str__(self):
        return self.title


class Color(models.Model):
    """
    Model representing predefined colors.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name="رنگ")

    def __str__(self):
        return self.name


class Car(models.Model):
    """
    مدل مربوط به آگهی خودرو
    """
    # general information of ads
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="فروشنده", related_name="cars")
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, verbose_name="نمایشگاه", related_name="cars",
                                   null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name="قیمت", null=True, blank=True)
    is_negotiable = models.BooleanField(default=True, verbose_name="قابل مذاکره")
    city = models.CharField(
        max_length=30, choices=PROVINCES, verbose_name="شهر", blank=True, null=True)
    sale_or_rent = models.CharField(max_length=255, choices=SALE_OR_RENT_CHOICES, verbose_name="فروشی یا اجاره‌ای",
                                    default="sale")
    # general information of car
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="برند", null=True)
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name="مدل خودرو", null=True)
    # optional
    promoted_model = models.CharField(max_length=255, verbose_name="مدل پیشنهادی ", null=True, blank=True)
    tire_condition = models.CharField(max_length=255, choices=TIRE_CONDITION_CHOICES, verbose_name="وضعیت لاستیک",
                                      null=True, blank=True)
    upholstery_condition = models.CharField(max_length=255, choices=UPHOLSTERY_CONDITION_CHOICES,
                                            blank=True, verbose_name="وضعیت مبلمان", null=True)

    year = models.PositiveIntegerField(verbose_name="سال ساخت")
    kilometer = models.PositiveIntegerField(verbose_name="کارکرد کیلومتر")
    body_type = models.CharField(max_length=255, choices=BODY_TYPE_CHOICES, verbose_name="نوع بدنه", null=True,
                                 blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, verbose_name="رنگ", null=True, blank=True)
    suggested_color = models.CharField(max_length=255, blank=True, null=True, verbose_name="رنگ پیشنهادی")
    fuel_type = models.CharField(max_length=255, choices=FUEL_TYPE_CHOICES, verbose_name="نوع سوخت")
    # Passenger Cars optional
    transmission = models.CharField(max_length=255, choices=TRANSMISSION_CHOICES, verbose_name="نوع گیربکس", null=True
                                    , blank=True)
    body_condition = models.CharField(
        max_length=255,
        choices=BODY_CONDITION_CHOICES,
        null=True, blank=True,
        verbose_name="وضعیت بدنه خودرو",
    )
    front_chassis_condition = models.CharField(
        max_length=255, choices=CHASSIS_CONDITION_CHOICES, default=("سالم", "سالم"), verbose_name="وضعیت شاسی جلو",
        null=True, blank=True
    )
    behind_chassis_condition = models.CharField(
        max_length=255, choices=CHASSIS_CONDITION_CHOICES, default=("سالم", "سالم"), verbose_name="وضعیت شاسی عقب",
        null=True, blank=True
    )

    # Heavyweights optional
    weight = models.IntegerField(verbose_name="وزن ماشین", null=True, blank=True)
    payload_capacity = models.IntegerField(verbose_name="حداکثر وزن ناخالص مجاز وسیله نقلیه", null=True, blank=True)
    wheel_number = models.SmallIntegerField(verbose_name="تعداد چرخ", default=4)
    # contact information
    phone_numbers = models.CharField(max_length=12, verbose_name="شماره تلفن")
    address = models.CharField(max_length=255, verbose_name="آدرس", null=True, blank=True)
    # ads status
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="pending", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    is_promoted = models.BooleanField(default=False, verbose_name="پیشنهادی")
    view_count = models.PositiveIntegerField(default=0)
    insurance = models.IntegerField(verbose_name='بیمه', validators=[MinValueValidator(0), MaxValueValidator(12)])
    is_urgent = models.BooleanField(default=False, verbose_name="فوری")

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
        indexes = [
            models.Index(fields=['brand', 'model']),
        ]

    def save(self, *args, **kwargs):
        if self.exhibition and not (self.user.roles == "EXHIBITOR"):
            raise ValidationError("این ماشین را نمیتوان در نمایشگاه ثبت کرد")
        if ((self.model is None) or (self.brand is None)) and self.promoted_model is None:
            raise ValidationError("شما باید فیلد های برند و مدل یا مدل پیشنهادی را پر کنید")
        # if not self.user.roles == "EXHIBITOR":
        #     if self.user.cars.filter(status="active").count() > 3:
        #         raise ValidationError("شما نمیتوانید بیشتر از سه ماشین ثبت کنید")
        if self.model.car_type == 'ماشین‌آلات سنگین' and not (
                self.weight or self.payload_capacity or self.wheel_number):
            raise ValidationError("شما باید مقادیر مربوط به ماشین سنگین را پر کنید")
        return super().save(*args, **kwargs)

    def clean(self):

        if (self.exhibition) and not (self.user.roles == "EXHIBITOR"):
            raise ValidationError("این ماشین را نمیتوان در نمایشگاه ثبت کرد")
        if ((self.model is None) or (self.brand is None)) and self.promoted_model is None:
            raise ValidationError("شما باید فیلد های برند و مدل یا مدل پیشنهادی را پر کنید")
        if self.model.car_type == 'ماشین‌آلات سنگین' and not (
                self.weight or self.payload_capacity or self.wheel_number):
            raise ValidationError("شما باید مقادیر مربوط به ماشین سنگین را پر کنید")
        return super().clean()

    def renew(self):
        if self.status == "expired":
            self.created_at = timezone.now()
            self.status = 'active'
            self.save()
        else:
            raise CustomValidationError({"": 'برای تمدید کردن اگهی وضعیت اگهی شما باید منقضی شده باشد'})

    def make_ad_global(self):
        self.city = "همه شهر ها"
        self.save()

    def make_ad_urgent(self):
        self.city = "همه شهر ها"
        self.save()

    def make_ad_promoted(self):
        self.is_promoted = True
        self.save()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"

    def __str__(self):
        return f"{self.user.username} - {self.car.brand.name} {self.car.model.title}"


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


class SelectedBrand(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, related_name='selected_brand',
                              verbose_name='برند منتخب')
    parent = models.CharField(max_length=40, choices=BRAND_PARENT_CHOICES, verbose_name='دسته بندی برند')

    def __str__(self):
        return f"{self.brand.name} - {self.parent}"

    class Meta:
        verbose_name = "برند منتخب"
        verbose_name_plural = "برندهای منتخب"


class SubscriptionPlans(models.Model):
    price = models.IntegerField(verbose_name='قیمت')
    amount = models.IntegerField(verbose_name='تعداد', default=1)
    name = models.CharField(max_length=255, verbose_name='اسم')
    type = models.CharField(max_length=255, choices=SUB_CHOICE, verbose_name="نوع اشتراک")
    description = models.TextField(verbose_name='توضیحات', null=True, blank=True)
    is_default = models.BooleanField(verbose_name='اشتراک پایه', default=False)

    class Meta:
        verbose_name = "اشتراک "
        verbose_name_plural = 'اشتراک ها'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    ad = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='ad_subscriptions', null=True, blank=True,
                           verbose_name='اگهی مربوطه')
    subscription_plan = models.ForeignKey(SubscriptionPlans, on_delete=models.SET_NULL, null=True,
                                          related_name='plan_subscriptions', )


class TransactionLog(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True,
                                     related_name='subscription_transactions', )
    amount = models.IntegerField(verbose_name='Amount')
    ref_id = models.CharField(max_length=255, verbose_name='Reference ID')
    status = models.CharField(max_length=50, verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.ref_id} - {self.status}"

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش ها"

    def apply(self):
        sub_type = self.subscription.subscription_plan.type
        ad, user = self.subscription.ad, self.subscription.user
        match sub_type:
            case 'extra_ad':
                user.extra_ads += self.amount
            case 'is_urgent':
                ad.make_ad_urgent()
            case 'is_promoted':
                ad.make_ad_promoted()
            case 'nationwide':
                ad.make_ad_global()
            case 'renew':
                ad.renew()
            case 'view_auction':
                user.profile.buy_view_auction_subscription(self.subscription.subscription_plan.amount)
            case 'submit_exhibition':
                user.make_user_exhibitor(self.subscription.subscription_plan.amount)
