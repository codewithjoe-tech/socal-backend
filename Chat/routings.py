from django.urls import re_path
from .consumers import ChatConsumer, SeenConsumer, NotifyConsumer, VideoCallConsumer,NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', ChatConsumer.as_asgi()),

    re_path(r'ws/chat/seen/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', SeenConsumer.as_asgi()),

    re_path(r'ws/call/notification/(?P<username>[A-Za-z0-9_\-=]+)/$', NotifyConsumer.as_asgi()),

    re_path(r'ws/invideo/call/(?P<username>[A-Za-z0-9_\-=]+)/$', VideoCallConsumer.as_asgi()),

    re_path(r'ws/notification/(?P<username>[A-Za-z0-9_\-=]+)/$', NotificationConsumer.as_asgi()),
]
