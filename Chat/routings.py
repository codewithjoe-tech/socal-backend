from django.urls import re_path
from .consumers import ChatConsumer, SeenConsumer, NotifyConsumer, VideoCallConsumer

websocket_urlpatterns = [
    # Chat messaging WebSocket
    re_path(r'ws/chat/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', ChatConsumer.as_asgi()),

    # Seen status WebSocket for chat
    re_path(r'ws/chat/seen/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', SeenConsumer.as_asgi()),

    # Call notification WebSocket
    re_path(r'ws/call/notification/(?P<username>[A-Za-z0-9_\-=]+)/$', NotifyConsumer.as_asgi()),

    # Video call WebSocket (signaling for video calls)
    re_path(r'ws/invideo/call/(?P<username>[A-Za-z0-9_\-=]+)/$', VideoCallConsumer.as_asgi()),
]
