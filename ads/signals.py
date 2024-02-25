from django.db.models.signals import post_save, post_delete
from haystack import signals
from django.db.models.signals import receiver

from ads.models import Car


@receiver(post_save, sender=Car)
def update_index(sender, instance, **kwargs):
    signals.update_index(sender, instance)


@receiver(post_delete, sender=Car)
def delete_index(sender, instance, **kwargs):
    signals.delete_index(sender, instance)
