from django.contrib import admin
from auction.models import Auction


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ["title","description"]
    search_fields = ["title","end_date","start_date","base_price"]
    list_filter = ["status"]
