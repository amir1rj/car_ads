
from auction.models import Auction
from celery import shared_task
from django.utils import timezone


@shared_task
def update_auction_status():
    """
    Updates the status of all expired auctions to 'ENDED'.
    """
    now = timezone.now()
    expired_auctions = Auction.objects.filter(status='ACTIVE', end_date__lt=now)
    for auction in expired_auctions:
        auction.status = 'ENDED'
        auction.save()

