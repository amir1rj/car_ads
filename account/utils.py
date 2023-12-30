import base64
import os
import re
from dataclasses import dataclass

import pyotp as pyotp
from rest_framework import serializers, permissions

from account import models
from account.models import  User

TOKEN_TYPE_CHOICE = (
    ("PASSWORD_RESET", "PASSWORD_RESET"),
)
ROLE_CHOICE = (
    ("ADMIN", "ADMIN"),
    ("EXHIBITOR", "EXHIBITOR"),
    ("CUSTOMER", "CUSTOMER"),

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

    raise serializers.ValidationError(f'{value} is not a valid phone')


def generate_otp()->int:
    totp = pyotp.TOTP(base64.b32encode(os.urandom(16)).decode('utf-8'))
    otp = totp.now()
    return otp


def is_admin_user(user:User)->bool:
    """
    Check an authenticated user is an admin or not
    """
    return user.is_admin


class IsAdmin(permissions.BasePermission):
    """Allows access only to Admin users."""
    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return models.is_admin_user(request.user)