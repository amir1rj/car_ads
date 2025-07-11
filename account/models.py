import uuid
from datetime import datetime, timedelta
from django.db import models
from account.managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, User
from account.utils import TOKEN_TYPE_CHOICE, ROLE_CHOICE, PROVINCES, LOGIN_TYPE_CHOICE
from car_ads import settings
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        verbose_name="نام کاربری",
        max_length=40,
        unique=True,
    )

    phone_number = models.CharField(max_length=12, verbose_name="شماره تلفن", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_admin = models.BooleanField(default=False, verbose_name="مدیر")
    roles = models.CharField(max_length=100, blank=True, choices=ROLE_CHOICE, default='CUSTOMER',
                             verbose_name="نقش")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="آخرین ورود")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    verified = models.BooleanField(default=False, verbose_name="تایید شده")
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'
    extra_ads = models.IntegerField(verbose_name='اگهی اضافه', default=0, blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

    def save_last_login(self) -> None:
        self.last_login = datetime.now()
        self.save()

    def make_user_exhibitor(self, days: int):
        now = timezone.now()
        date = timedelta(days=days)
        if self.roles != 'EXHIBITOR':
            self.roles = 'EXHIBITOR'
            self.profile.exhibition_expire_time = now + date
        else:
            self.profile.exhibition_expire_time += date
        self.save()


class PendingUser(models.Model):
    phone = models.CharField(max_length=20, verbose_name="شماره تلفن")
    username = models.CharField(max_length=50, null=True, blank=True, verbose_name="نام کاربری")
    verification_code = models.CharField(max_length=8, blank=True, null=True, verbose_name="کد تأیید")
    password = models.CharField(max_length=255, null=True, verbose_name="رمز عبور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        verbose_name = "کاربر در انتظار"
        verbose_name_plural = "کاربران در انتظار"

    def __str__(self):
        return f"{str(self.phone)} {self.verification_code}"

    def is_valid(self) -> bool:
        """5 mins OTP validation"""
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60)

        now = timezone.now()
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر")
    token = models.CharField(max_length=8, verbose_name="توکن")
    token_type = models.CharField(max_length=100, choices=TOKEN_TYPE_CHOICE, verbose_name="نوع توکن")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")

    class Meta:
        verbose_name = "توکن"
        verbose_name_plural = "توکن‌ها"

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def is_valid(self) -> bool:
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60)
        now = timezone.now()
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def reset_user_password(self, password: str) -> None:
        self.user.set_password(password)
        self.user.save()


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="کاربر"
    )
    email = models.EmailField(verbose_name="ایمیل", max_length=255, unique=True, null=True, blank=True)
    picture = models.ImageField(
        upload_to=f"images/profiles/{user}/",
        default="images/profiles/default/default.jpeg",
        verbose_name="تصویر پروفایل",
    )
    city = models.CharField(
        max_length=30, choices=PROVINCES, verbose_name="شهر", blank=True, null=True
    )
    first_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="نام")
    last_name = models.CharField(max_length=255, verbose_name="نام خانوادگی", blank=True, null=True)
    gender = models.CharField(
        max_length=3, choices=(("مرد", "مرد"), ("زن", "زن")), verbose_name="جنسیت", null=True, blank=True
    )
    view_auction = models.BooleanField(default=False, verbose_name='دیدن مزایده')
    view_auction_expire_time = models.DateTimeField(blank=True, null=True,
                                                    verbose_name='تاریخ انقضای اشتراک دیدن مزایده ')
    exhibition_expire_time = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضای نمایشگاه')

    def buy_view_auction_subscription(self, days: int, ) -> None:
        now = timezone.now()
        date = timedelta(days=days)
        # if user has view auction role it would increase days and if it has not it will add this and set days
        if not self.view_auction:
            self.view_auction_expire_time = now + date
            self.view_auction = True
        else:
            self.view_auction_expire_time += date
        self.save()

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"

    def handle_expire_times(self):
        now = timezone.now()
        if self.user.roles == 'EXHIBITOR' and self.exhibition_expire_time and self.exhibition_expire_time <= now:
            self.user.roles = "CUSTOMER"
        if self.view_auction and self.view_auction_expire_time and self.view_auction_expire_time <= now:
            self.view_auction = False
        self.save()
        self.user.save()


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=255, choices=LOGIN_TYPE_CHOICE)
    browser = models.CharField(max_length=255, null=True, blank=True)
    operating_system = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.type}  {self.user}  from {self.ip_address} at {self.timestamp}"
