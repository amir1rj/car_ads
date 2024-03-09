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

    },
    "delete_pending_users": {
        "task": "account.tasks.delete_pending_users",
        "schedule": crontab(hour=0, minute=0),

    },
    "update_ads_status": {
        "task": "ads.tasks.update_ads_status",
        "schedule": crontab(hour=0, minute=0),

    },

}
