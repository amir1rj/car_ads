from datetime import datetime,timedelta
from celery import shared_task
from django.utils import timezone
from ads.models import Car


@shared_task
def send_sms(message):
    print(message)


@shared_task
def update_ads_status():
    """
   Update status of cas from active to inactive
    """

    date_30_days_ago = timezone.now() - timedelta(days=30)
    cars = Car.objects.filter(created_at__lt=date_30_days_ago)
    for car in cars:
        car.status = "inactive"
        car.save()
