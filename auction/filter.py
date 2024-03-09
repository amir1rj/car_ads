from django_filters import FilterSet
from auction.models import Auction


class AuctionFilter(FilterSet):
    class Meta:
        model = Auction
        fields = ["city"]
