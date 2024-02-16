from django.db.models.signals import post_save
from account.models import User, Profile
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    print("salam")
    if created:
        print("boro")
        Profile.objects.create(user=instance, **kwargs)


post_save.connect(create_profile, sender=User)
