from rest_framework.routers import DefaultRouter
from ads.views import AdViewSets
app_name = 'ad'

router = DefaultRouter()

urlpatterns = [

]
router.register(r'', AdViewSets, basename='main')
urlpatterns += router.urls