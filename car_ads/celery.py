import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "car_ads.settings")
app = Celery('car_ads')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    "update_auction_status": {
        "task": "auction.tasks.update_auction_status",
        "schedule": crontab(hour=0, minute=0),

    }

}
