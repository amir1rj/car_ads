from rest_framework import serializers

from auction.models import Auction


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        exclude = ('search_vector',)


class RetrieveAuctionSerializer(AuctionSerializer):
    related_auctions = serializers.SerializerMethodField()

    class Meta(AuctionSerializer.Meta):
        exclude = ('search_vector',)
        extra_fields = ['related_auctions']
    def get_related_auctions(self, obj):
        # Start with auctions that have the same city and type
        related_auctions = Auction.objects.filter(
            auction_type=obj.auction_type,
            city=obj.city
        ).exclude(id=obj.id)

        # If there are less than 8, add more auctions that match the type only
        if related_auctions.count() < 8:
            more_auctions = Auction.objects.filter(
                auction_type=obj.auction_type
            ).exclude(id=obj.id).exclude(id__in=related_auctions.values_list('id', flat=True))
            related_auctions = related_auctions | more_auctions

        # If there are still less than 8, add auctions that match the city only
        if related_auctions.count() < 8:
            even_more_auctions = Auction.objects.filter(
                city=obj.city
            ).exclude(id=obj.id).exclude(id__in=related_auctions.values_list('id', flat=True))
            related_auctions = related_auctions | even_more_auctions

        # Limit the result to 8 auctions
        return AuctionSerializer(related_auctions.distinct()[:8], many=True).data
