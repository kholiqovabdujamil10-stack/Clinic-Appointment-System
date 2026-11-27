from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import *


@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        group = Group.objects.filter(name='Users').first()

        if group:
            instance.groups.add(group)