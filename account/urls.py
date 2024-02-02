from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from account.views import UserViewSets, AuthViewSets, PasswordChangeView,ProfileViewSets

app_name = 'user'

router = DefaultRouter()

urlpatterns = [

    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
router.register(r'users', UserViewSets, basename='user')
router.register(r"auth", AuthViewSets,  basename="auth")
router.register("profile",ProfileViewSets ,  basename="profile")
router.register("change-password", PasswordChangeView, basename="password-change")
urlpatterns += router.urls
