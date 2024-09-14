from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'
    verbose_name = "اعلان ها"

    def ready(self):
        from notification.signals import notify_user_on_status_change
