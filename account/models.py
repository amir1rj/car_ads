import uuid
from datetime import datetime, timezone

from django.contrib.auth import models

from django.db import models
from django.utils.timezone import now

from account.managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,User
from django.utils.translation import gettext_lazy as _

from account.utils import TOKEN_TYPE_CHOICE, ROLE_CHOICE, default_role
from car_ads import settings


class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(
        verbose_name=_('username'),
        max_length=40,
        unique=True,
    )
    email = models.EmailField(
        verbose_name=_("email"),
        max_length=255,
        unique=True,
        null=True, blank=True
    )
    phone_number = models.CharField(max_length=12, verbose_name=_("phone number"),unique=True )
    is_active = models.BooleanField(default=True, verbose_name=_("activity"),)
    is_admin = models.BooleanField(default=False , verbose_name=_("admin"))
    roles = models.CharField(max_length=20, blank=True, choices=ROLE_CHOICE, default=default_role)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    firstname = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
    profile = models.ImageField(null=True, blank=True, )
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def save_last_login(self) -> None:
        self.last_login = datetime.now()
        self.save()

class PendingUser(models.Model):
    phone = models.CharField(max_length=20)
    verification_code = models.CharField(max_length=8, blank=True, null=True)
    password = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.phone)} {self.verification_code}"

    def is_valid(self) -> bool:
        """10 mins OTP validation"""
        lifespan_in_seconds = float(settings.OTP_EXPIRE_TIME * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=8)
    token_type = models.CharField(max_length=100, choices=TOKEN_TYPE_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def is_valid(self) -> bool:
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60 )
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def reset_user_password(self, password: str) -> None:
        self.user.set_password(password)
        self.user.save()


