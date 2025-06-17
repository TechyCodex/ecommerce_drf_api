from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def set_user_type(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        if instance.user_type != 'admin':
            instance.user_type = 'admin'
            instance.save()
