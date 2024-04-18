from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets, ExhibitionViewSet, LatestVideosList, BrandModelsView
from django.urls import path

app_name = 'ad'

router = DefaultRouter()

router.register(r'exhibition', ExhibitionViewSet, basename='exhibition')
urlpatterns = [

    path('latest-videos/', LatestVideosList.as_view(), name='latest_videos_list'),
    path('brand-models/', BrandModelsView.as_view(), name='brand_models_list'),

]
router.register(r'', AdViewSets, basename='main')

urlpatterns += router.urls
