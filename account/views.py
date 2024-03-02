from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import User, Token, Profile
from account.permisions import IsOwnerOrReadOnly
from account.serializers import CreateUserSerializer, ListUserSerializer, UpdateUserSerializer, UserNameSerializer, \
    AccountVerificationSerializer, InitiatePasswordResetSerializer, CreatePasswordFromResetOTPSerializer, \
    PasswordChangeSerializer, ProfileSerializer
from account.utils import TokenEnum, is_admin_user, IsAdmin


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
        return Response({"success": True, "message": "OTP sent for verification!"}, status=200)


class AuthViewSets(viewsets.GenericViewSet):
    """Auth viewSets"""
    serializer_class = UserNameSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["initiate_password_reset", "create_password", "verify_account"]:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=AccountVerificationSerializer,
        url_path="verify-account",
    )
    def verify_account(self, request, pk=None):
        """Activate a user account using the verification(OTP) sent to the user phone"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Account Verification Successful"}, status=200)

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
                         "message": "Temporary password sent to your mobile!"}, status=200)

    @action(methods=['POST'], detail=False, serializer_class=CreatePasswordFromResetOTPSerializer,
            url_path='create-password')
    def create_password(self, request, pk=None):
        """Create a new password given the reset OTP sent to user phone number"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token: Token = Token.objects.filter(
            token=request.data['otp'], token_type=TokenEnum.PASSWORD_RESET).first()
        if not token or not token.is_valid():
            return Response({'success': False, 'errors': 'Invalid password reset otp'}, status=400)
        token.reset_user_password(request.data['new_password'])
        token.delete()
        return Response({'success': True, 'message': 'Password successfully reset'}, status=status.HTTP_200_OK)


class PasswordChangeView(viewsets.GenericViewSet):
    '''Allows password change to authenticated user'''
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        context = {"request": request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Your password has been updated."}, status.HTTP_200_OK)


class ProfileViewSets(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Profile.objects.all()

    def update(self, request, pk=None, **kwargs):
        instance = Profile.objects.get(id=pk)
        self.check_object_permissions(request, instance)
        data = request.data.copy()
        # حذف ایمیل از داده ها در صورت عدم تغییر
        if data.get('email') == instance.email:
            del request.data['email']

        serializer = ProfileSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response({"response": " your profile updated"}, status.HTTP_200_OK)
        return Response({"response": serializer.errors})

    def create(self, request, **kwargs):
        serializer = ProfileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.validated_data["user"] = request.user
            serializer.save()
            return Response({"response": "done"})
        return Response({"response": serializer.errors})

