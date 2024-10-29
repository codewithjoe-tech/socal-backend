from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from rest_framework import status
from . serializers import *
from django.contrib.auth import get_user_model
from .utils import *
from django.db.models import Count,Q



User = get_user_model()







class ChatRooms(APIView):
    def get(self,request,username):
        try:
            other_user = User.objects.get(username=username)
            current_user = request.user
            chat_room_name = generate_chatroom_name([current_user,other_user])

            chat_room,created  = Chatroom.objects.get_or_create(name=chat_room_name)
            if created:
                ChatroomUser.objects.create(chatroom=chat_room,user=current_user)
                ChatroomUser.objects.create(chatroom=chat_room,user=other_user)

            serializer = ChatRoomSerializer(chat_room,context={'request':request})
            



            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
   
from django.db.models import Count, Q

class ChatRoomList(APIView):
    def get(self, request):
        try:
            current_user = request.user
            
            deleted_chatroom_ids = ChatRoomDeleted.objects.filter(user=current_user, disabled=False).values_list('chatroom_id', flat=True)

            chat_rooms = Chatroom.objects.filter(
                chatroom_users__user=current_user
            ).annotate(
                message_count=Count('messages')
            ).filter(
                message_count__gt=0
            ).exclude(
                Q(id__in=deleted_chatroom_ids) 
            )

            serializer = ChatRoomSerializer(chat_rooms, many=True, context={'request': request})
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ChatRoomSpecific(APIView):
    def get(self,request,name):
        try:
            chat_room = Chatroom.objects.get(name=name)
            if not chat_room.chatroom_users.filter(user=request.user).exists():
                return Response({"error": "Unauthorized Access"}, status=status.HTTP_403_FORBIDDEN)
            serializer = ChatRoomSerializer(chat_room, context={'request':request})
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GetMessages(APIView):
    def get(self, request,chatroom):
        chatroom = Chatroom.objects.get(name=chatroom)
        if not chatroom.chatroom_users.filter(user=request.user).exists():
            return Response({"error": "Unauthorized Access"}, status=status.HTTP_403_FORBIDDEN)
        
        messages = Message.objects.filter(chatroom=chatroom).order_by('timestamp')
        serializer = MessageSerializer(messages,many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    


    def post(self, request):
        data = request.data
        chatroom_id = data.get('chatroom')
        content_type = data.get('content_type')
        sender = request.user

        try:
            chatroom = Chatroom.objects.get(name=chatroom_id)
        except Chatroom.DoesNotExist:
            return Response({"error": "Chatroom does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Select the right s    erializer based on content_type

        print(data)
        if content_type == 'textmessage':
            serializer = TextMessageSerializer(data=data)
        elif content_type == 'imagemessage':
            serializer = ImageMessageSerializer(data=request.FILES)
        elif content_type == 'videomessage':
            serializer = VideoMessageSerializer(data=request.FILES)
        elif content_type == 'audiomessage':
            serializer = AudioMessageSerializer(data=request.FILES)
        else:
            return Response({"error": "Invalid content type."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            content_object = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        content_type_obj = ContentType.objects.get_for_model(content_object)

        message = Message.objects.create(
            chatroom=chatroom,
            sender=sender,
            content_type=content_type_obj,
            object_id=content_object.id
        )

        message_serializer = MessageSerializer(message)
        return Response(message_serializer.data, status=status.HTTP_201_CREATED)
