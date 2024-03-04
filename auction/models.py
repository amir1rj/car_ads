from datetime import timezone, datetime
from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    image = models.ImageField(upload_to='auction_images', verbose_name="تصویر")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")

    # فیلدهای جدید
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت پایه")
    status = models.CharField(max_length=255, choices=[('ACTIVE', 'فعال'), ('ENDED', 'پایان یافته')], default='ACTIVE',
                              verbose_name="وضعیت")

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
