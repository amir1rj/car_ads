from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets, ExhibitionViewSet, LatestVideosList, ExhibitionVideoViewSet, ImageViewSet, \
    BrandModelsView, BrandListView, CarPriceStatsView, SelectedBrandListView, CheckSubmitAddAuthorization, \
    FavoriteViewSet, ColorListView, BrandByTypeAPIView, RenewAd, ZarinpalPaymentView, SubscriptionPlansListView, \
    ZarinpalPaymentVerifyView, SubscriptionCreateView
from django.urls import path, include

app_name = 'ad'

router = DefaultRouter()
exhibition_video_router = DefaultRouter()
exhibition_video_router.register(r'videos', ExhibitionVideoViewSet, basename='exhibition-video')
router.register(r'exhibition', ExhibitionViewSet, basename='exhibition')
car_image_router = DefaultRouter()
car_image_router.register(r'images', ImageViewSet, basename='car-image')
urlpatterns = [
    path('brand-models/', BrandModelsView.as_view(), name='brand_models_list'),
    path('brands/', BrandListView.as_view(), name='brand_list'),
    path('price-stats/', CarPriceStatsView.as_view(), name='price-stats'),
    path('latest-videos/', LatestVideosList.as_view(), name='latest_videos_list'),
    path('exhibitions/<int:exhibition_pk>/', include(exhibition_video_router.urls)),
    path('cars/<int:car_pk>/', include(car_image_router.urls)),
    path('selected-brands/<str:parent>/', SelectedBrandListView.as_view(), name='selected-brands-list'),
    path('check-athorization', CheckSubmitAddAuthorization.as_view(), name="check-user-create-add-authorization"),
    path('colors/', ColorListView.as_view(), name='color-list'),
    path('brand_type/', BrandByTypeAPIView.as_view(), name='brand_type'),
    path('renew_ad/<int:id>/', RenewAd.as_view(), name='renew_ad'),
    path('payment/', ZarinpalPaymentView.as_view(), name='zarinpal_payment'),
    path('subscription-plans/', SubscriptionPlansListView.as_view(), name='subscription-plans-list'),
    path('subscription-create/', SubscriptionCreateView.as_view(), name='subscription-create'),
    path('verify-payment', ZarinpalPaymentVerifyView.as_view(), name='zarinpal_payment_verify'),

]

router.register(r'', AdViewSets, basename='main')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
urlpatterns += router.urls
