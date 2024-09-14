from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

# ایجاد یک روتر برای ثبت ViewSetها
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # شامل کردن مسیرهای روتر
    path('', include(router.urls)),
]
