from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/seen/(?P<chatroom_name>[A-Za-z0-9_\-=]+)/$', SeenConsumer.as_asgi()),

    # Video Chat

      re_path(r'ws/call/notification/(?P<username>[A-Za-z0-9_\-=]+)/$', NotifyConsumer.as_asgi()),


]
