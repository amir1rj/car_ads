from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets,ExhibitionViewSet
from django.urls import path, include

app_name = 'ad'

router = DefaultRouter()

router.register(r'exhibition',ExhibitionViewSet , basename='exhibition')
urlpatterns = [

]
router.register(r'', AdViewSets, basename='main')


urlpatterns += router.urls
