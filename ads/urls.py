from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets, ExhibitionViewSet, LatestVideosList, ExhibitionVideoViewSet, ImageViewSet
from django.urls import path, include

app_name = 'ad'

router = DefaultRouter()
exhibition_video_router = DefaultRouter()
exhibition_video_router.register(r'videos', ExhibitionVideoViewSet, basename='exhibition-video')
router.register(r'exhibition', ExhibitionViewSet, basename='exhibition')
car_image_router = DefaultRouter()
car_image_router.register(r'images', ImageViewSet, basename='car-image')
urlpatterns = [

    path('latest-videos/', LatestVideosList.as_view(), name='latest_videos_list'),
    path('exhibitions/<int:exhibition_pk>/', include(exhibition_video_router.urls)),
    path('cars/<int:car_pk>/', include(car_image_router.urls)),
]
router.register(r'', AdViewSets, basename='main')

urlpatterns += router.urls
