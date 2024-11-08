from . models import Notification
from django.db.models.signals import post_save , pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from . serializers import NotificationSerilaizer


@receiver(post_save , sender=Notification)
def send_asyn_notification(sender, instance , created, **kwargs):
    print("Working")
    if created:
        channel_layer = get_channel_layer()
        group_name = f"notification_{instance.user.username}"

        serialized_data = NotificationSerilaizer(instance).data


        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type':'send_notification',
                'data':json.dumps(serialized_data)
            }
        )
