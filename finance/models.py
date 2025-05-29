from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from finance.utils import SUB_CHOICE, STATUS_CHOICE
from ads.models import Car


# Create your models here.
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_subscriptions')
    ad = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='ad_subscriptions', null=True, blank=True,
                           verbose_name='اگهی مربوطه')
    subscription_plan = models.ForeignKey(SubscriptionPlans, on_delete=models.SET_NULL, null=True,
                                          related_name='plan_subscriptions', )


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_payments',
                             verbose_name='کاربر')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True,
                                     verbose_name='اشتراک', related_name='subscription_payments')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, verbose_name='وضعیت پرداخت', default=0)
    amount = models.IntegerField(verbose_name='مقدار')
    ref_id = models.CharField(max_length=255, verbose_name='Reference ID')
    created_at = models.DateTimeField(auto_now_add=True)
    authority = models.CharField(max_length=255, verbose_name='Authority', unique=True)

    def __str__(self):
        return f"Transaction {self.ref_id} - {self.status}"

    class Meta:
        verbose_name = "صورت حساب"
        verbose_name_plural = "صورت حساب ها"

    def apply(self):
        sub_type = self.subscription.subscription_plan.type
        ad, user = self.subscription.ad, self.user
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
