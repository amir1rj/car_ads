from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    verbose_name = "کاربران"

    def ready(self):
        from account.signals import log_user_login,log_user_logout,log_user_login_failed
