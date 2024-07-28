from celery import shared_task
from django.db import transaction
from account.models import PendingUser
from django.utils import timezone
from datetime import timedelta
from kavenegar import *
import requests

API_KEY = "7150623768587371314335626843775455477949473769785655642B456E38554137637A5979456E6143593D"


@shared_task
def send_sms(message_info):
    token, phone = message_info.get("message"), message_info.get("phone")
    url = f"https://api.kavenegar.com/v1/{API_KEY}/verify/lookup.json"
    template = "verify"
    params = {
        'receptor': phone,
        'token': token,
        'template': template
    }
    response = requests.get(url, params=params)
    return response.json()


@shared_task
def delete_pending_users():
    """
    Delete expired pending users records in database.
    """

    expired_otp_tokens = PendingUser.objects.all()
    for p_user in expired_otp_tokens:
        if not p_user.is_valid():
            p_user.delete()
