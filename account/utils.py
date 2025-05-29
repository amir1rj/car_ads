import base64
import os
import re
from dataclasses import dataclass
import pyotp as pyotp
from rest_framework import serializers, permissions
from account.models import User
import uuid


def generate_free_transaction_uuid():
    """
    Generates a string in the format 'free transaction {uuid}'.

    :return: A string like 'free transaction 123e4567-e89b-12d3-a456-426614174000'
    """
    return f"free transaction {uuid.uuid4()}"


PROVINCES = [("آذربایجان شرقی", "آذربایجان شرقی"),
             ("آذربایجان غربی", "آذربایجان غربی"),
             ("اصفهان", "اصفهان"),
             ("البرز", "البرز"),
             ("ایلام", "ایلام"),
             ("بوشهر", "بوشهر"),
             ("تهران", "تهران"),
             ("چهارمحال و بختیاری", "چهارمحال و بختیاری"),
             ("خراسان جنوبی", "خراسان جنوبی"),
             ("خراسان رضوی", "خراسان رضوی"),
             ("خراسان شمالی", "خراسان شمالی"),
             ("خوزستان", "خوزستان"),
             ("زنجان", "زنجان"),
             ("سمنان", "سمنان"),
             ("سیستان و بلوچستان", "سیستان و بلوچستان"),
             ("فارس", "فارس"),
             ("قزوین", "قزوین"),
             ("قم", "قم"),
             ("کردستان", "کردستان"),
             ("کرمان", "کرمان"),
             ("کرمانشاه", "کرمانشاه"),
             ("کهگیلویه و بویراحمد", "کهگیلویه و بویراحمد"),
             ("گلستان", "گلستان"),
             ("لرستان", "لرستان"),
             ("گیلان", "گیلان"),
             ("همدان", "همدان"),
             ("یزد", "یزد"),
             ("همه شهر ها", "همه شهر ها"),
             ]
TOKEN_TYPE_CHOICE = (
    ("PASSWORD_RESET", "PASSWORD_RESET"),
)
ROLE_CHOICE = (
    ("EXHIBITOR", "EXHIBITOR"),
    ("CUSTOMER", "CUSTOMER"),

)
LOGIN_TYPE_CHOICE = (
    ("login", "login"),
    ("logout", "logout"),
    ("login_failed", "login_failed"),
)


def default_role():
    return ["CUSTOMER"]


@dataclass
class SystemRoleEnum:
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    EXHIBITOR = "EXHIBITOR"


@dataclass
class TokenEnum:
    PASSWORD_RESET = "PASSWORD_RESET"


def check_message(message):
    return message


def check_phone(value):
    """
    Validate the phone number based on Iranian format
    :param: a string
    :return: True/False
    """
    patter1 = re.compile("^9\d{9}$")
    patter2 = re.compile("^09\d{9}$")
    patter3 = re.compile("^00989\d{9}$")
    patter4 = re.compile("^\+989\d{9}$")

    if bool(patter1.match(value)):
        return "0" + value
    if bool(patter2.match(value)):
        return value
    if bool(patter3.match(value)):
        return "0" + value[4:]
    if bool(patter4.match(value)):
        return "0" + value[3:]

    raise serializers.ValidationError(f'{value} شماره نا معتبر است')


def generate_otp() -> int:
    totp = pyotp.TOTP(base64.b32encode(os.urandom(16)).decode('utf-8'))
    otp = totp.now()
    return otp


def is_admin_user(user: User) -> bool:
    """
    Check an authenticated user is an admin or not
    """
    return user.is_admin


class IsAdmin(permissions.BasePermission):
    """Allows access only to Admin users."""
    message = "فقط ادمین میتواند این عمل را اجرا کند"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_admin_user(request.user)


def validate_password_strength(value):
    """Validates password strength."""

    if not any(char.isdigit() for char in value):
        raise serializers.ValidationError("رمز عبور شما باید حداقل  شامل یک عدد باشد", code="easy password")
    if not any(char.islower() for char in value):
        raise serializers.ValidationError("رمزعبور شما باید حداقل  شامل یک حرف کوچک باشد", code="easy password")
    if not any(char.isupper() for char in value):
        raise serializers.ValidationError("رمزعبور شما باید حداقل شامل یک حرف بزرگ باشد", code="easy password")
    return value
