from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets
from django.urls import path, include

app_name = 'ad'

router = DefaultRouter()

urlpatterns = [

]
router.register(r'', AdViewSets, basename='main')

urlpatterns += router.urls
