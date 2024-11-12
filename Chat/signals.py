from django.db.models import Count, Q,Max
from django.core.exceptions import ObjectDoesNotExist
from . models import Notification , Message , ChatroomUser , ChatRoomDeleted , Chatroom
from django.db.models.signals import post_save , pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from . serializers import NotificationSerilaizer,ChatRoomSerializer


class DummyRequest:
    def __init__(self, user):
        self.user = user

@receiver(post_save , sender=Notification)
def send_asyn_notification(sender, instance , created, **kwargs):
    print("Working")
    if created:
        channel_layer = get_channel_layer()
        group_name = f"notification_{instance.user.username}"

        serialized_data = NotificationSerilaizer(instance).data

        print(serialized_data)

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type':'send_notification',
                'data':serialized_data
            }
        )

@receiver(post_save, sender=Message)
def send_chat_list_ws(sender, instance, **kwargs):
    try:
        chatroom = instance.chatroom
        chatroom_users = ChatroomUser.objects.filter(chatroom=chatroom)
        print(chatroom_users)
        channel_layer = get_channel_layer()

        for chatroom_user in chatroom_users:
            print(chatroom_user)
            user = chatroom_user.user

            # if user is None:
            #     print("user is none skipping")
            #     continue

            deleted_chatroom_ids = ChatRoomDeleted.objects.filter(
                user=user, disabled=False
            ).values_list('chatroom_id', flat=True)

            chat_rooms = Chatroom.objects.filter(
                chatroom_users__user=user
            ).annotate(
                message_count=Count('messages'),
                latest_message_time=Max('messages__timestamp')
            ).filter(
                message_count__gt=0
            ).exclude(
                Q(id__in=deleted_chatroom_ids)
            ).order_by('-latest_message_time')
            request = DummyRequest(user)
            serializer = ChatRoomSerializer(chat_rooms, many=True, context={'request': request})
            serialized_data = serializer.data

            group_name = f"chatlist_{user.username}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_chat_list',
                    'data': serialized_data
                }
            )
    except ObjectDoesNotExist as e:
        print(f"Chatroom or User does not exist: {e}")
    except Exception as e:
        print(f"Error sending chat list notification: {e}")
