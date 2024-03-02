import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "car_ads.settings")
app = Celery('car_ads')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


# app.conf.beat_schedule = {
#     "my_task_in_every_day": {
#         "task": "cart.tasks.check_coupon_expire_date",
#         "schedule": 60 * 60 * 24
#
#     }
#
# }


CELERY_BEAT_SCHEDULE = {
    'update_auction_status': {
        'task': 'auctions.tasks.update_auction_status',
        'schedule': crontab(minute=0, hour=0),
    },
}
