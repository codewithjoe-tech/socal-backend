# ASGI configuration
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from .channelsmiddleware import JWTAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

django.setup()

from Chat.routings import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
