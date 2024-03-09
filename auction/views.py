from rest_framework import viewsets
from rest_framework.response import Response
from auction.filter import AuctionFilter
from auction.serializers import AuctionSerializer
from auction.models import Auction
from account.permisions import ReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter


class AuctionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuctionSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        return Auction.get_active_auctions(self)

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(name='city', description='Filter by car city.', required=False, type=str),

        ],

    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_set = AuctionFilter(request.GET, queryset=queryset)
        filtered_queryset = filter_set.qs
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)
