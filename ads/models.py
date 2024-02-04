from django.db import models
from account.models import User
from ads.constants import *
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("brand name"))

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name


class CarModel(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Car model'))
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="models", verbose_name=_('Brand'))

    class Meta:
        verbose_name = _('model')
        verbose_name_plural = _('models')

    def __str__(self):
        return self.title


# مدل مربوط به آگهی خودرو
class Car(models.Model):
    """
    مدل مربوط به آگهی خودرو
    """
    # اطلاعات کلی
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("seller"), related_name="cars")
    title = models.CharField(max_length=255, verbose_name=_("title"), )
    description = models.TextField(verbose_name=_("description"), )
    price = models.PositiveIntegerField(verbose_name=_("price"))
    is_negotiable = models.BooleanField(default=True, verbose_name=_("is negotiable"))

    # اطلاعات خودرو
    car_type = models.CharField(max_length=255, choices=CAR_TYPE_CHOICES, verbose_name=_("car type"))
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name=_("brand"))
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT, verbose_name=_("car model"))
    year = models.PositiveIntegerField(verbose_name=_("year "))
    kilometer = models.PositiveIntegerField(verbose_name=_("Mileage kilometers"))
    body_type = models.CharField(max_length=255, choices=BODY_TYPE_CHOICES, verbose_name=_("body type"))
    color = models.CharField(max_length=255, verbose_name="رنگ")
    transmission = models.CharField(max_length=255, choices=TRANSMISSION_CHOICES, verbose_name=_("transmission type"))
    fuel_type = models.CharField(max_length=255, choices=FUEL_TYPE_CHOICES, verbose_name=_("fuel type"))
    vin = models.CharField(max_length=255, verbose_name=_("vin"))
    inspection_date = models.DateField(verbose_name=_('inspection date'))

    # اطلاعات تماس
    phone_numbers = models.CharField(max_length=12, verbose_name=_("phone number"))
    address = models.CharField(max_length=255, verbose_name=_("address"))

    # تصاویر
    images = models.ManyToManyField('Image', verbose_name=_("images"))

    # وضعیت آگهی
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="pending", verbose_name=_("status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    is_promoted = models.BooleanField(default=False, verbose_name=_("is promoted"))

    def __str__(self):
        return f"{self.title} ({self.brand} {self.model})"

    class Meta:
        ordering = ['-created_at', '-is_promoted']
        verbose_name = _('car')
        verbose_name_plural = _('cars')
        get_latest_by = "created_at"


class Image(models.Model):
    ad = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="ad_images", null=True)
    title = models.CharField(max_length=30)
    image = models.ImageField(upload_to="ads")

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return self.title


class Feature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="features")  # Add this line
    name = models.CharField(max_length=255, verbose_name=_("features name"))

    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('features')

    def __str__(self):
        return self.name
