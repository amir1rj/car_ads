from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from account.exceptions import CustomValidationError
from auction.filter import AuctionFilter
from auction.pagination import AuctionPagination
from auction.serializers import AuctionSerializer, RetrieveAuctionSerializer
from auction.models import Auction
from account.permisions import ReadOnly, HasViewAuction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import IsAuthenticated


class AuctionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuctionSerializer
    permission_classes = [HasViewAuction]
    pagination_class = AuctionPagination


    def get_queryset(self):
        return Auction.get_active_auctions(self)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RetrieveAuctionSerializer
        return AuctionSerializer

    @extend_schema(
        description="Search for ads based on various filters.",
        parameters=[
            OpenApiParameter(
                name='city',
                description='Filter by auction city.',
                required=False,
                type=str
            ), OpenApiParameter(
                name='search',
                description='search auctions by their names and descriptions.',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='auction_type',
                description='Filter by auction type (multiple types can be separated by commas).',
                required=False,
                type=str,
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='Filter for miscellaneous auctions',
                        description='Filter auctions that are miscellaneous',
                        value='متفرقه'
                    ),
                    OpenApiExample(
                        'Example 2',
                        summary='Filter for property auctions',
                        description='Filter auctions that are for property',
                        value='ملک'
                    ),
                    OpenApiExample(
                        'Example 3',
                        summary='Filter for car auctions',
                        description='Filter auctions that are for cars',
                        value='ماشین'
                    ),
                ]
            ), OpenApiParameter(
                name='base_price_min',
                type=str,
                description=' minimum base_price ',

            ), OpenApiParameter(
                name='base_price_max',
                type=str,
                description='maximum base_price ',

            ),
        ]
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
