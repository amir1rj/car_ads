from datetime import datetime, timezone
from account.tasks import send_sms
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers
import re
from account.models import User, PendingUser, Token, Profile
from account.utils import check_phone, generate_otp, TokenEnum, is_admin_user, validate_password_strength
from django.contrib.auth import user_logged_in
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ads.models import Car, Exhibition

from ads.serializers import AdSerializer

from ads.pagination import CustomPagination


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'roles')


class ExhibitonDemo(serializers.ModelSerializer):
    class Meta:
        model = Exhibition
        fields = "__all__"


class JWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict):
        user = User.objects.filter(phone_number=attrs.get("phone_number")).first()
        if user:
            user_logged_in.send(sender=user.__class__, request=self.context['request'], user=user)
        return super().validate(attrs)


class CreateUserSerializer(serializers.Serializer):
    """Serializer for creating user object"""
    phone_number = serializers.CharField(required=True, allow_blank=False)
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(min_length=6)

    def validate_username(self, value):
        """Validates username format and uniqueness."""
        username_regex = r"^[a-zA-Z0-9_]+$"  # Only letters, numbers, and underscores
        if not re.match(username_regex, value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.",
                                              code="Invalid username")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.", "existed username")
        return value

    def validate_password(self, value):
        """Validates password strength."""
        # Implement your password strength requirements here
        validate_password_strength(value)
        return value

    def validate(self, attrs: dict):
        phone_number, username = attrs.get('phone_number'), attrs.get('username')
        strip_number = phone_number.lower().strip()
        cleaned_number = check_phone(strip_number)
        if User.objects.filter(phone_number__iexact=cleaned_number).exists():
            raise serializers.ValidationError(
                {'phone': 'Phone number already exists'})
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        attrs['phone'] = cleaned_number
        return super().validate(attrs)

    def create(self, validated_data: dict):
        otp = generate_otp()
        phone_number, username = validated_data.get('phone'), validated_data.get('username')
        user, _ = PendingUser.objects.update_or_create(
            phone=phone_number, username=username,
            defaults={
                "phone": phone_number,
                "verification_code": otp,
                "username": username,
                "password": make_password(validated_data.get('password')),
                "created_at": datetime.now(timezone.utc)
            }
        )
        message_info = {
            'message': f"Account Verification!\nYour OTP for BotoApp is {otp}.\nIt expires in 5 minutes",
            'phone': user.phone
        }
        send_sms.delay(message_info)

        return user


class AccountVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs: dict):
        phone_number: str = attrs.get('phone_number').strip().lower()
        mobile: str = check_phone(phone_number)
        pending_user: PendingUser = PendingUser.objects.filter(
            phone=mobile, verification_code=attrs.get('otp')).first()
        if pending_user:
            if not pending_user.is_valid():  # Check token lifespan
                raise serializers.ValidationError(
                    {'otp': 'Verification failed. OTP has expired.'})
            attrs['phone'] = mobile
            attrs['password'] = pending_user.password
            attrs['pending_user'] = pending_user
            attrs["username"] = pending_user.username
        else:
            raise serializers.ValidationError(
                {'otp': 'Verification failed. Invalid OTP or number'})
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data: dict):
        validated_data.pop('otp')
        pending_user = validated_data.pop('pending_user')
        user = User.objects.create_user_with_phone(validated_data)
        Profile.objects.get_or_create(user=user)
        pending_user.delete()
        return validated_data


class InitiatePasswordResetSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs: dict):
        phone = attrs.get('phone')
        strip_number = phone.lower().strip()
        cleaned_number = check_phone(strip_number)
        user = User.objects.filter(phone_number=cleaned_number, is_active=True).first()

        if not user:
            raise serializers.ValidationError({'phone': 'Phone number not registered.'})
        attrs['phone'] = cleaned_number
        attrs['user'] = user
        return super().validate(attrs)

    def create(self, validated_data):
        phone = validated_data.get('phone')
        user = validated_data.get('user')
        otp = generate_otp()
        token, _ = Token.objects.update_or_create(
            user=user,
            token_type=TokenEnum.PASSWORD_RESET,
            defaults={
                "user": user,
                "token_type": TokenEnum.PASSWORD_RESET,
                "token": otp,
            }
        )

        message_info = {
            'message': f"Password Reset!\nUse {otp} to reset your password.\nIt expires in 5 minutes",
            'phone': phone
        }

        send_sms.delay(message_info)
        return token


class CreatePasswordFromResetOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        """Validates password strength """

        validate_password_strength(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=False)
    new_password = serializers.CharField(max_length=128, min_length=5)

    def validate(self, attrs):
        new_password, old_password = attrs.get("new_password"), attrs.get("old_password")
        if old_password == new_password:
            raise serializers.ValidationError({"new_password": "New password cannot be same as old password."})
        return super().validate(attrs)

    def validate_old_password(self, value):
        request = self.context["request"]
        if not request.user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validates password strength """

        validate_password_strength(value)
        return value

    def save(self):
        user: User = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save(update_fields=["password"])


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            'phone_number',
            "verified",
            "created_at",
            "roles",
        ]

        extra_kwargs = {
            "verified": {"read_only": True},
            "roles": {"read_only": True},
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            'username',
            "verified",
            "roles"
        ]
        extra_kwargs = {
            "last_login": {"read_only": True},
            "verified": {"read_only": True},
            "roles": {"required": False},
        }

    def validate(self, attrs: dict):
        """Only allow admin to modify/assign role"""
        auth_user: User = self.context["request"].user
        new_role_assignment = attrs.get("roles", None)
        if new_role_assignment and is_admin_user(auth_user):
            pass
        else:
            attrs.pop('roles', None)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        """Prevent user from updating password"""
        if validated_data.get("password", False):
            validated_data.pop('password')
        instance = super().update(instance, validated_data)
        return instance


class UserNameSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=255)


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    cars = serializers.SerializerMethodField(read_only=True)
    exhibition = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"

    def validate(self, attrs):
        email = attrs.get('email')
        if email is not None:
            if Profile.objects.filter(email=email).exists():
                raise serializers.ValidationError("your email is already exists")
        return attrs

    def update(self, instance, validated_data):
        """
        آپدیت نمونه پروفایل موجود بر اساس داده های ارائه شده.

        - فیلدهای اختیاری را با بررسی وجود آنها در `validated_data` مدیریت می کند.
        - اعتبارسنجی منحصر به فرد بودن ایمیل را با در نظر گرفتن نمونه فعلی تضمین می کند.
        """

        # تکرار در تمام فیلدها و آپدیت فقط موارد موجود در `validated_data`
        for field, value in validated_data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        # بررسی خاص برای آپدیت ایمیل
        if 'email' in validated_data:
            email = validated_data['email']
            if email and email != instance.email:
                if Profile.objects.filter(email=email).exclude(pk=instance.pk).exists():
                    raise serializers.ValidationError("پروفایل با این ایمیل از قبل موجود است")

        instance.save()
        return instance

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        if Profile.objects.get(user=validated_data.get("user")) is not None:
            raise serializers.ValidationError("پروفایل از قبل وجود دارد ")
        return Profile.objects.get_or_create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        print("-" * 100)
        print(request)
        method = request.resolver_match.url_name
        if method in ['profile-list', ]:
            representation.pop('cars')

        return representation

    def get_cars(self, obj):
        request = self.context.get('request')
        if request.user == obj.user:
            cars = Car.objects.filter(user=obj.user)
        else:
            cars = Car.objects.filter(status="active").filter(user=obj.user)

        paginator = CustomPagination()
        paginated_cars = paginator.paginate_queryset(cars, self.context['request'])
        serializer = AdSerializer(paginated_cars, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data).data

    def get_exhibition(self, obj):
        request = self.context.get('request')
        if request.user == obj.user:
            exh = Exhibition.objects.filter(user=obj.user)
        else:
            exh = Exhibition.objects.filter(is_deleted=False).filter(user=obj.user)
        return ExhibitonDemo(exh, many=True).data

    def get_user(self, obj):
        user = obj.user
        return UserSerializer(user).data
