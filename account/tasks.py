import time
from car_ads.celery import app
from celery import shared_task


@shared_task
def send_sms():
    print(" ")

