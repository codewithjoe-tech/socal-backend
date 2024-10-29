import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from Chat.models import *
from django.contrib.contenttypes.models import ContentType
from Chat.serializers import *
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from asgiref.sync import sync_to_async

User = get_user_model()


BASE_URL = "http://127.0.0.1:8000"
def build_absolute_uri(path):
    protocol = 'https' if settings.USE_HTTPS else 'http'
    domain = get_current_site(None).domain 
    return f"{protocol}://{domain}{path}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.user = self.scope["user"]
        self.chatroom_group_name = f"chat_{self.chatroom_name.replace('=', '')}"
        chatroom = await self.get_chatroom(self.chatroom_name)

        if not await self.is_user_in_chatroom(chatroom, self.user):
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.chatroom_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chatroom_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        
        data = json.loads(text_data)
        message_type = data.get('message_type')
        content_type = data.get('content_type')
        content_data = data.get('content')

        chatroom = await self.get_chatroom(self.chatroom_name)

        if not await self.is_user_in_chatroom(chatroom, self.user):
            return

        if message_type == "file":
            
            await self.receive_file( content_data)
        else:
          
            await self.handle_text_message(content_type, content_data, chatroom)

    async def receive_file(self,  content_data):
        message = await self.get_message_by_id(content_data)
        message_data = await self.serialize_message(message)
        await self.channel_layer.group_send(
            self.chatroom_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )

    async def handle_text_message(self, content_type, content_data, chatroom):
    
        content_object = await self.handle_content_creation(content_type, content_data)

        if content_object:
            content_type_obj = await self.get_content_type_for_model(content_object)

            message = await self.create_message(
                chatroom=chatroom,
                sender=self.user,
                content_type=content_type_obj,
                object_id=content_object.id
            )

            message_data = await self.serialize_message(message)

            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

    async def chat_message(self, event):
       
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_chatroom(self, chatroom_name):
        
        return Chatroom.objects.get(name=chatroom_name)

    @database_sync_to_async
    def is_user_in_chatroom(self, chatroom, user):
     
        return chatroom.chatroom_users.filter(user=user).exists()

    @database_sync_to_async
    def create_message(self, chatroom, sender, content_type, object_id):
        chatroom_user = ChatroomUser.objects.filter(chatroom=chatroom).exclude(user=sender).first()
        online_status = chatroom_user.in_chat
        message =  Message.objects.create(
            chatroom=chatroom,
            sender=sender,
            content_type=content_type,
            object_id=object_id,
            seen=online_status
        )
        return message
        

    @database_sync_to_async
    def save_content(self, serializer):
        
        return serializer.save()

  

    @database_sync_to_async
    def serialize_message(self, message):
        
        
        return MessageSerializer(message).data

    @database_sync_to_async
    def get_content_type_for_model(self, content_object):
        
        return ContentType.objects.get_for_model(content_object)

    async def handle_content_creation(self, content_type, content_data):
    
        serializers = {
            'textmessage': TextMessageSerializer,
            'imagemessage': ImageMessageSerializer,
            'videomessage': VideoMessageSerializer,
            'audiomessage': AudioMessageSerializer,
        }

        serializer_class = serializers.get(content_type)

        if serializer_class:
            serializer = serializer_class(data=content_data)
            if serializer.is_valid():
                return await self.save_content(serializer)
        return None
    

    @database_sync_to_async
    def get_message_by_id(self, message_id):
        chatroom = Chatroom.objects.get(name=self.chatroom_name)
        message = Message.objects.get(id=message_id)
        chatroom_user = ChatroomUser.objects.filter(chatroom=chatroom).exclude(user=self.user).first()
        if chatroom_user.in_chat:
            message.seen=True
            message.save()
        return message




class SeenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.user = self.scope['user']
        self.chatroom_group_name = f"seen_{self.chatroom_name.replace('=', '')}"
        chatroom = await self.get_chatroom(self.chatroom_name)

        if not await self.is_user_in_chatroom(chatroom, self.user):
            await self.close()
        else:
            self.status = await self.update_online_status(self.user, chatroom)
            await self.channel_layer.group_add(self.chatroom_group_name, self.channel_name)
            await self.accept()
            print("seen connection established!")

            message_ids = await self.update_message_status(chatroom)
            if message_ids:
                await self.send_message_seen(message_ids)

    async def disconnect(self, code):
        chatroom = await self.get_chatroom(self.chatroom_name)
        self.status = await self.make_user_offline(self.user, chatroom)
        await self.channel_layer.group_discard(self.chatroom_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        return super().receive(text_data, bytes_data)

    async def update_message_status(self, chatroom):
        message_ids = await self.get_unseen_message_ids(chatroom)
        if self.status:
            await self.mark_messages_as_seen(chatroom)
        return message_ids

    async def send_message_seen(self, message_ids):
        await self.channel_layer.group_send(
            self.chatroom_group_name,
            {
                'type': 'message_seen',
                'seen_message_ids': message_ids
            }
        )

    async def message_seen(self, event):
        await self.send(text_data=json.dumps({
            'seen_message_ids': event['seen_message_ids']
        }))

    @database_sync_to_async
    def get_chatroom(self, chatroom_name):
        return Chatroom.objects.get(name=chatroom_name)

    @database_sync_to_async
    def is_user_in_chatroom(self, chatroom, user):
        return chatroom.chatroom_users.filter(user=user).exists()

    @database_sync_to_async
    def update_online_status(self, user, chatroom):
        chatroom_user = ChatroomUser.objects.get(chatroom=chatroom, user=user)
        chatroom_user.in_chat = True
        chatroom_user.save()
        return chatroom_user.in_chat

    @database_sync_to_async
    def make_user_offline(self, user, chatroom):
        chatroom_user = ChatroomUser.objects.get(chatroom=chatroom, user=user)
        chatroom_user.in_chat = False
        chatroom_user.save()
        return chatroom_user.in_chat

    @database_sync_to_async
    def get_unseen_message_ids(self, chatroom):
        return list(Message.objects.filter(chatroom=chatroom, seen=False)
                    .exclude(sender=self.user)
                    .values_list('id', flat=True))

    @database_sync_to_async
    def mark_messages_as_seen(self, chatroom):
        Message.objects.filter(chatroom=chatroom, seen=False).exclude(sender=self.user).update(seen=True)




class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.username = self.user.username
        self.group_name = f"notify_{self.username}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'call_request':
            target_username = data.get('target_username')
            if self.username != target_username:
                profile_picture = await self.get_profile_picture(self.user)
                await self.channel_layer.group_send(
                    f"notify_{target_username}",
                    {
                        'type': 'send_call_request',
                        'from': self.username,
                        'profile_picture': profile_picture,
                    }
                )

        elif action == 'accept_call':
            target_username = data.get('target_username')
            if target_username:
                await self.channel_layer.group_send(
                    f"notify_{target_username}",
                    {
                        'type': 'send_call_accept',
                        'from': self.username
                    }
                )

        elif action == 'reject':
            target_username = data.get('target_username')
            await self.channel_layer.group_send(
                f"notify_{target_username}",
                {
                    'type': 'send_call_end',
                    'from': self.username
                }
            )

    async def send_call_request(self, event):
        await self.send(text_data=json.dumps({
            'type': 'CALL_REQUEST',
            'from': event['from'],
            'profile_picture': event.get('profile_picture', '/user.png')
        }))

    async def send_call_accept(self, event):
        await self.send(text_data=json.dumps({
            'type': 'CALL_ACCEPTED',
            'from': event['from']
        }))

    async def send_call_end(self, event):
        await self.send(text_data=json.dumps({
            'type': 'CALL_REJECTED',
            'from': event['from']
        }))

    @sync_to_async
    def get_profile_picture(self, user):
        if hasattr(user, 'profile') and user.profile.profile_picture:
            return f"{BASE_URL}{user.profile.profile_picture.url}"
        return "/user.png"