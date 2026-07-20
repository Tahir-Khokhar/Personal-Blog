from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User
from apps.profiles.models import Profile


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
