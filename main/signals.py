from django.db.models.signals import post_save
from django.dispatch import receiver
import textwrap

from .models import AdditionalInfo

@receiver(post_save, sender=AdditionalInfo)
def post_save_create_rsvp(sender, instance, created, **kwargs):
    name = textwrap.shorten(instance.last_name, width=3, placeholder='')
    customer_code = name.upper() + "00" + str(instance.id)
    if created:
        instance.customer_code = customer_code
        instance.save()