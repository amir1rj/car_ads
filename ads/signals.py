from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from haystack import signals
from django.db.models.signals import post_save

from account.logging_config import logger
from account.models import User, Profile
from ads.models import Car, Exhibition
from notification.models import Notification


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, **kwargs)


post_save.connect(create_profile, sender=User)


@receiver(post_save, sender=Car)
def update_index(sender, instance, **kwargs):
    signals.update_index(sender, instance)


@receiver(post_delete, sender=Car)
def delete_index(sender, instance, **kwargs):
    signals.delete_index(sender, instance)


@receiver(post_save, sender=Exhibition)
def update_index(sender, instance, **kwargs):
    signals.update_index(sender, instance)


@receiver(post_delete, sender=Exhibition)
def delete_index(sender, instance, **kwargs):
    signals.delete_index(sender, instance)

