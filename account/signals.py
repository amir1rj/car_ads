from datetime import datetime, timezone
from account.models import Log
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']
    timestamp = datetime.now(timezone.utc)
    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os

    Log.objects.create(
        user=user,
        ip_address=ip_address,
        timestamp=timestamp,
        type='login',
        browser=browser,
        operating_system=operating_system,
    )


@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']
    timestamp = datetime.now(timezone.utc)
    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os
    Log.objects.create(
        user=user,
        ip_address=ip_address,
        timestamp=timestamp,
        type='logout',
        browser=browser,
        operating_system=operating_system,
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip_address = request.META['REMOTE_ADDR']
    timestamp = datetime.now(timezone.utc)
    browser = request.user_agent.browser.family
    operating_system = request.user_agent.os
    Log.objects.create(
        user=None,  # No user object available for failed logins
        ip_address=ip_address,
        timestamp=timestamp,
        type='login_failed',
        browser=browser,
        operating_system=operating_system,
    )
