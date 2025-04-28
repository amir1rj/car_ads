from account.models import Log
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.db.models.signals import post_save
from account.models import User, Profile
from ads.models import SubscriptionPlans, Subscription, TransactionLog


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        subscription_plans = SubscriptionPlans.objects.filter(is_default=True)
        for plan in subscription_plans:
            subscription = Subscription.objects.create(plan=plan, user=instance)
            transaction = TransactionLog.objects.create(
                subscription=subscription,
                amount=0,
                ref_id="free",
                status='Success'
            )
            transaction.apply()


post_save.connect(create_profile, sender=User)


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']

    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os

    Log.objects.create(
        user=user,
        ip_address=ip_address,

        type='login',
        browser=browser,
        operating_system=operating_system,
    )


@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']

    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os
    Log.objects.create(
        user=user,
        ip_address=ip_address,

        type='logout',
        browser=browser,
        operating_system=operating_system,
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']

    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os
    Log.objects.create(
        user=None,  # No user object available for failed logins
        ip_address=ip_address,

        type='login_failed',
        browser=browser,
        operating_system=operating_system,
    )
