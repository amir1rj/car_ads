from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from account.models import User, Token, Profile
from account.permisions import IsOwnerOrReadOnly
from account.serializers import CreateUserSerializer, ListUserSerializer, UpdateUserSerializer, UserNameSerializer, \
    AccountVerificationSerializer, InitiatePasswordResetSerializer, CreatePasswordFromResetOTPSerializer, \
    PasswordChangeSerializer, ProfileSerializer, JWTSerializer
from account.utils import TokenEnum, is_admin_user, IsAdmin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.views import APIView


@method_decorator(ratelimit(key='ip', rate='20/h', block=True, method='POST'), name='post')
@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = JWTSerializer


@extend_schema(tags=['Authentication'])
@method_decorator(ratelimit(key='ip', rate='20/h', method='POST'), name='post')
class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for handling token refresh with rate limiting and documentation.
    """
    pass


@extend_schema_view(
    list=extend_schema(tags=['Users']),
    retrieve=extend_schema(tags=['Users']),
    create=extend_schema(tags=['Users']),
    partial_update=extend_schema(tags=['Users']),
    destroy=extend_schema(tags=['Users']),
)
class UserViewSets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        user: User = self.request.user
        if is_admin_user(user):
            return super().get_queryset().all()
        return super().get_queryset().filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        if self.action in ["partial_update", "update"]:
            return UpdateUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["create"]:
            permission_classes = [AllowAny]
        elif self.action in ["list", "retrieve", "partial_update", "update"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["destroy"]:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "کد تایید با موفقیت ارسال شد"}, status=200)


@extend_schema_view(
    verify_account=extend_schema(tags=['Authentication']),
    initiate_password_reset=extend_schema(tags=['Authentication']),
    create_password=extend_schema(tags=['Authentication']),
)
class AuthViewSets(viewsets.GenericViewSet):
    """Auth viewSets"""
    serializer_class = UserNameSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["initiate_password_reset", "create_password", "verify_account"]:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @method_decorator(ratelimit(key='ip', rate='20/h', method='POST'))
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=AccountVerificationSerializer,
        url_path="verify-account",
    )
    def verify_account(self, request):
        """Activate a user account using the verification(OTP) sent to the user phone"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "حساب شما با موفقیت اهراز هویت شد"}, status=200)

    @method_decorator(ratelimit(key='user', rate='20/h', method='POST'))
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=InitiatePasswordResetSerializer,
        url_path="initiate-password-reset",
    )
    def initiate_password_reset(self, request, pk=None):
        """Send temporary OTP to user phone to be used for password reset"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True,
                         "message": "کد تایید به شماره تلفن شما ارسال شد"}, status=200)

    @action(methods=['POST'], detail=False, serializer_class=CreatePasswordFromResetOTPSerializer,
            url_path='create-password')
    def create_password(self, request, pk=None):
        """Create a new password given the reset OTP sent to user phone number"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token: Token = Token.objects.filter(
            token=request.data['otp'], token_type=TokenEnum.PASSWORD_RESET).first()
        if not token or not token.is_valid():
            return Response({'success': False, 'errors': 'کد تایید نا معتبر'}, status=400)
        token.reset_user_password(request.data['new_password'])
        token.delete()
        return Response({'success': True, 'message': 'رمز عبور شما با موفقیت بروزرسانی شد'}, status=status.HTTP_200_OK)


@extend_schema_view(
    create=extend_schema(tags=['Authentication']),

)
class PasswordChangeView(viewsets.GenericViewSet):
    '''Allows password change to authenticated user'''
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='20/h', method='POST'))
    def create(self, request, *args, **kwargs):
        context = {"request": request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'message': 'رمز عبور شما با موفقیت بروزرسانی شد '}, status.HTTP_200_OK)


class ProfileViewSets(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Profile.objects.all()

    def retrieve(self, request, pk=None, **kwargs):
        user = User.objects.get(id=pk)
        instance = Profile.objects.get(id=user.profile.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, pk=None, **kwargs):
        user = User.objects.get(id=pk)
        instance = Profile.objects.get(id=user.profile.id)
        self.check_object_permissions(request, instance)
        data = request.data.copy()
        if data.get('email') == instance.email:
            del request.data['email']
        serializer = ProfileSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response({"response": "پروفایل شما با موفقیت بروزرسانی شد"}, status.HTTP_200_OK)
        return Response({"response": serializer.errors})

    def create(self, request, **kwargs):
        serializer = ProfileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({"response": "done"}, status=status.HTTP_201_CREATED)
        return Response({"response": serializer.errors})


class GetUserId(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response({"id": request.user.id}, status=status.HTTP_200_OK)
        else:
            return Response("اطلاعات هویتی یافت نشد", status=status.HTTP_401_UNAUTHORIZED)
