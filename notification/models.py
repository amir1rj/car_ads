from django.db import models
from account.models import User
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    Represents a notification that can be sent to a user or all users.
    """
    MESSAGE_TYPE_CHOICES = [
        ('welcome', 'پیام خوش‌آمدگویی'),
        ('ad_posted', 'تشکر بابت ثبت آگهی'),
        ('broadcast', 'پیام برادکست'),
        ('custom', 'سفارشی'),
        ('status_change', "تغییر وضعیت")
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True,
                                  verbose_name='کاربر')
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES, default='custom',
                                    verbose_name='نوع پیام')
    message = models.TextField(verbose_name='محتوای پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    def __str__(self):
        return f"{self.message_type} to {self.recipient.username if self.recipient else 'All users'}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "اعلان"
        verbose_name_plural = 'اعلان ها'


class BroadcastNotification(models.Model):
    """
    Stores broadcast messages to be sent to all users.
    """
    message = models.TextField("محتوای پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')

    def __str__(self):
        return f"Broadcast created at {self.created_at}"

    class Meta:
        verbose_name = "اعلان پخش همگانی"
        verbose_name_plural = "اعلان های پخش همگانی"
