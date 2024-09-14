from django_filters import FilterSet, CharFilter
from django_filters.filters import BaseInFilter
from auction.models import Auction


class CharInFilter(BaseInFilter, CharFilter):
    pass


class AuctionFilter(FilterSet):
    auction_type = CharInFilter(field_name='auction_type', lookup_expr='in')

    class Meta:
        model = Auction
        fields = ['city', 'auction_type']
