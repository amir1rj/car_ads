from datetime import timezone, datetime
from django.db import models
from account.utils import PROVINCES
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db.models import F

AUCTION_TYPES = [
    ('متفرقه', 'متفرقه'),
    ('ملک', 'ملک'),
    ('ماشین', 'ماشین'),
]


class Auction(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to='auction_images', verbose_name="تصویر", null=True, blank=True)
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت پایه")
    status = models.CharField(max_length=255, choices=[('ACTIVE', 'فعال'), ('ENDED', 'پایان یافته')], default='ACTIVE',
                              verbose_name="وضعیت")
    city = models.CharField(
        max_length=30, choices=PROVINCES, verbose_name="شهر", blank=True, null=True)
    auction_type = models.CharField(max_length=255, choices=AUCTION_TYPES, verbose_name="نوع مزایده", default="ماشین")
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "مزایده ها"
        verbose_name = "مزایده"

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = datetime.now(timezone.utc)
        return self.start_date <= now <= self.end_date

    def get_active_auctions(self):
        now = datetime.now(timezone.utc)
        return Auction.objects.filter(status='ACTIVE', end_date__gt=now)
