
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reels
from .tasks import generate_thumbnail_for_reel

@receiver(post_save, sender=Reels)
def create_thumbnail_on_save(sender, instance, created, **kwargs):
    if created and not instance.thumbnail:
        generate_thumbnail_for_reel.delay(instance.id)