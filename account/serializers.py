from datetime import datetime, timezone

from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers

from account.models import User, PendingUser, Token
from account.utils import check_phone, generate_otp, TokenEnum, is_admin_user


class CreateUserSerializer(serializers.Serializer):
    """Serializer for creating user object"""
    phone_number = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(min_length=6)

    def validate(self, attrs: dict):
        phone_number = attrs.get('phone_number')
        strip_number = phone_number.lower().strip()
        cleaned_number = check_phone(strip_number)
        if User.objects.filter(phone_number__iexact=cleaned_number).exists():
            raise serializers.ValidationError(
                {'phone': 'Phone number already exists'})
        attrs['phone'] = cleaned_number
        return super().validate(attrs)
    # def create(self, validated_data):
    #     phone_number = validated_data.get('phone_number')
    #     password= validated_data.get('password')
    #     user= User.objects.create_user(phone_number=phone_number,password=password)
    #     return user
    def create(self, validated_data: dict):
        otp = generate_otp()
        phone_number = validated_data.get('phone')
        user, _ = PendingUser.objects.update_or_create(
            phone=phone_number,
            defaults={
                "phone": phone_number,
                "verification_code": otp,
                "password": make_password(validated_data.get('password')),
                "created_at": datetime.now(timezone.utc)
            }
        )
        message_info = {
            'message': f"Account Verification!\nYour OTP for BotoApp is {otp}.\nIt expires in 10 minutes",
            'phone': user.phone
        }
        # send_phone_notification.delay(message_info)
        print(message_info)
        return user


class AccountVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs: dict):
        phone_number: str = attrs.get('phone_number').strip().lower()
        mobile: str = check_phone(phone_number)
        pending_user: PendingUser = PendingUser.objects.filter(
            phone=mobile, verification_code=attrs.get('otp')).first()
        if pending_user and pending_user.is_valid():
            attrs['phone'] = mobile
            attrs['password'] = pending_user.password
            attrs['pending_user'] = pending_user
        else:
            raise serializers.ValidationError(
                {'otp': 'Verification failed. Invalid OTP or Number'})
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data: dict):
        validated_data.pop('otp')
        pending_user = validated_data.pop('pending_user')
        User.objects.create_user_with_phone(**validated_data)
        pending_user.delete()
        return validated_data


class InitiatePasswordResetSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs: dict):
        phone = attrs.get('phone')
        strip_number = phone.lower().strip()
        mobile = check_phone(strip_number)
        user = User().objects.filter(phone=mobile, is_active=True).first()
        if not user:
            raise serializers.ValidationError({'phone': 'Phone number not registered.'})
        attrs['phone'] = mobile
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
                "created_at": datetime.now(timezone.utc)
            }
        )

        message_info = {
            'message': f"Password Reset!\nUse {otp} to reset your password.\nIt expires in 10 minutes",
            'phone': phone
        }

        # send_phone_notification.delay(message_info)
        print(message_info)
        return token

class CreatePasswordFromResetOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=False)
    new_password = serializers.CharField(max_length=128, min_length=5)

    def validate_old_password(self, value):
        request = self.context["request"]

        if not request.user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
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
            "firstname",
            "lastname",
            "email",
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
            "firstname",
            "lastname",
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
    username = serializers.CharField(required=True,max_length=255)


