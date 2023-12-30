from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.views import UserViewSets, AuthViewSets, PasswordChangeView

app_name = 'user'

router = DefaultRouter()
router.register(r'users', UserViewSets, basename='user')
urlpatterns = [
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]

router.register(r"auth", AuthViewSets,  basename="auth")
router.register("change-password", PasswordChangeView, basename="password-change")
urlpatterns += router.urls
