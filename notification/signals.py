from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from account.logging_config import logger
from ads.models import Car
from notification.tasks import send_personal_notification


@receiver(pre_save, sender=Car)
def notify_user_on_status_change(sender, instance, **kwargs):
    """
    Send a notification to the user if the status of the car ad changes.
    """
    """
    Send a notification to the user if the status of the car ad changes.
    """
    if instance._state.adding:
        return

    if instance.pk:
        # Get the previous instance from the database
        old_instance = sender.objects.get(pk=instance.pk)
        # Compare the old and new status
        if old_instance.status != instance.status:
            # Use get_FOO_display() to show the human-readable (translated) status
            old_status_display = old_instance.get_status_display()
            new_status_display = instance.get_status_display()

            message = f"وضعیت آگهی شما از '{old_status_display}' به '{new_status_display}' تغییر کرده است."
            logger.info(f"old status: {old_status_display}, new status: {new_status_display}")
            # Create a notification for the user
            send_personal_notification(instance.user, message, "status_change")


@receiver(post_save, sender=Car)
def notify_user_on_create(sender, instance, created, **kwargs):
    """
    Send a notification to the user when a new car ad is created.
    """
    if created:
        # آگهی برای اولین بار ثبت شده است
        message = "درخواست شما با موفقیت ثبت شد و در حال بررسی است."
        send_personal_notification(instance.user, message, "ad_posted")
