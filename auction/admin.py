from django.contrib import admin
from auction.models import Auction


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ["title"]
