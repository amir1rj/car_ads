from rest_framework.routers import DefaultRouter
from auction.views import AuctionViewSet

app_name = 'auction'

router = DefaultRouter()

router.register(r'', AuctionViewSet, basename='auction')
urlpatterns = []

urlpatterns += router.urls
