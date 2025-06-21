# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def restore_inventory_on_cancel(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        for item in instance.items.all():
            item.product.inventory.quantity_available += item.quantity
            item.product.inventory.save()
