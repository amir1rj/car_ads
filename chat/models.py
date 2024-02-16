import uuid

from account.models import User
from django.db import models
from ads.models import Car


# Create your models here.


class Chat(models.Model):
    roomName = models.CharField(max_length=50, verbose_name="نام اتاق چت", unique=True)
    users = models.ManyToManyField(User, verbose_name="کاربران")
    max_users = models.PositiveIntegerField(default=2, verbose_name="حداکثر کاربران")

    def clean(self, *args, **kwargs):
        if self.users.count() > self.max_users:
            raise ValueError("تعداد کاربران چت از حد مجاز بیشتر است")
        super().save(*args, **kwargs)

    def __str__(self):
        usernames = [user.username for user in self.users.all()]
        return " ,".join(usernames)

    class Meta:
        verbose_name = "چت"
        verbose_name_plural = "چت‌ها"


class Chat_Image(models.Model):
    image = models.ImageField(upload_to='images', blank=True, null=True, verbose_name="تصویر")
    chat = models.ForeignKey(Chat, null=True, blank=True, related_name='images', on_delete=models.CASCADE,
                             verbose_name="چت")

    class Meta:
        verbose_name = "تصویر چت"
        verbose_name_plural = "تصاویر چت"


class Message(models.Model):
    content = models.TextField(verbose_name="محتوای پیام")
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="نویسنده پیام")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages", verbose_name="چت")

    def last_messages(self, roomName):
        return Message.objects.order_by('-timestamp').filter(chat__roomName=roomName)

    def __str__(self):
        return self.author.username

    class Meta:
        verbose_name = "پیام"
        verbose_name_plural = "پیام‌ها"
