from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django_filters import FilterSet, CharFilter, RangeFilter
from django_filters.filters import BaseInFilter
from auction.models import Auction


class CharInFilter(BaseInFilter, CharFilter):
    pass


class AuctionFilter(FilterSet):
    auction_type = CharInFilter(field_name='auction_type', lookup_expr='in')
    city = CharFilter(field_name='city', lookup_expr='exact')
    search = CharFilter(method='filter_by_search')
    base_price = RangeFilter()

    class Meta:
        model = Auction
        fields = ['city', 'auction_type', 'search', 'base_price']

    def filter_by_search(self, queryset, name, value):
        search_query = SearchQuery(value)
        # Use the search_vector field for full-text search
        queryset = queryset.annotate(rank=SearchRank(F('search_vector'), search_query)) \
            .filter(search_vector=search_query) \
            .order_by('-rank')
        return queryset
