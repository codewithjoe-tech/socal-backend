import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from Chat.models import Chatroom, Message, TextMessage, ImageMessage, VideoMessage, AudioMessage
from django.contrib.contenttypes.models import ContentType
from Chat.serializers import MessageSerializer, TextMessageSerializer, ImageMessageSerializer, VideoMessageSerializer, AudioMessageSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

User = get_user_model()



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
            
            await self.receive_file(content_type, content_data)
        else:
          
            await self.handle_text_message(content_type, content_data, chatroom)

    async def receive_file(self, content_type, content_data):
        """
        Handle receiving a file through WebSocket.
        The content_data here should be a base64 encoded file from the frontend.
        """
        import base64
        from django.core.files.base import ContentFile

        # Decoding the base64 encoded file
        file_data = base64.b64decode(content_data['file_data'])
        file_name = content_data['file_name']

        if content_type == "imagemessage":
            file_instance = ImageMessage(image=ContentFile(file_data, name=file_name))
        elif content_type == "videomessage":
            file_instance = VideoMessage(video=ContentFile(file_data, name=file_name))
        elif content_type == "audiomessage":
            file_instance = AudioMessage(audio=ContentFile(file_data, name=file_name))
        else:
            return

        # Save the file to the database
        content_object = await self.save_file_content(file_instance)

        if content_object:
            content_type_obj = await self.get_content_type_for_model(content_object)
            chatroom = await self.get_chatroom(self.chatroom_name)

            message = await self.create_message(
                chatroom=chatroom,
                sender=self.user,
                content_type=content_type_obj,
                object_id=content_object.id
            )

            message_data = await self.serialize_message(message)

            # Broadcast the new message to the group
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

    async def handle_text_message(self, content_type, content_data, chatroom):
        """
        Handle sending a text message.
        """
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

            # Broadcast the new message to the group
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
        """
        Check if a user is part of the given chatroom.
        """
        return chatroom.chatroom_users.filter(user=user).exists()

    @database_sync_to_async
    def create_message(self, chatroom, sender, content_type, object_id):
        """
        Create a new message in the database.
        """
        return Message.objects.create(
            chatroom=chatroom,
            sender=sender,
            content_type=content_type,
            object_id=object_id
        )

    @database_sync_to_async
    def save_content(self, serializer):
        
        return serializer.save()

    @database_sync_to_async
    def save_file_content(self, file_instance):
        
        file_instance.save()
        return file_instance

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
