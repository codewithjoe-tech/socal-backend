from django.urls import path
from .views import *


urlpatterns = [
    path('chat-room/<username>',ChatRooms.as_view()),
    path('chat-room/specific/<name>',ChatRoomSpecific.as_view()),
    path('chatroom-list/', ChatRoomList.as_view()),
    path('get-messages/',GetMessages.as_view()),
    path('get-messages/<chatroom>',GetMessages.as_view()),
]
