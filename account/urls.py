from django.urls import path
from rest_framework.routers import DefaultRouter

from account.views import UserViewSets, AuthViewSets, PasswordChangeView, ProfileViewSets, CustomTokenObtainPairView, \
    GetUserId, CustomTokenRefreshView

app_name = 'user'
# ratelimit(key='ip', method='POST', rate='3/h')
router = DefaultRouter()

urlpatterns = [

    path('token', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('get-user-id', GetUserId.as_view(), name='get-user-id'),
]
router.register(r'users', UserViewSets, basename='user')
router.register(r"auth", AuthViewSets, basename="auth")
router.register("profile", ProfileViewSets, basename="profile")
router.register("change-password", PasswordChangeView, basename="password-change")
urlpatterns += router.urls
