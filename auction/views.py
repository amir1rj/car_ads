from rest_framework import viewsets
from auction.serializers import AuctionSerializer
from auction.models import Auction
from account.permisions import ReadOnly


class AuctionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuctionSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        return Auction.get_active_auctions(self)
