from celery import shared_task
from django.db import transaction
from account.models import PendingUser
from django.utils import timezone
from datetime import timedelta
@shared_task
def send_sms(message):
    print(message)


@shared_task
def delete_pending_users():
    """
    Delete expired pending users records in database.
    """

    expired_otp_tokens = PendingUser.objects.all()
    for p_user in expired_otp_tokens:
        if not p_user.is_valid():
            p_user.delete()


