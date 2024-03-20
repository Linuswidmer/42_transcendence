import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# from pong.routing import websocket_urlpatterns

from django.urls import path
from pong.consumers import MultiplayerConsumer
websocket_urlpatterns = [
    path('ws/pong/<room_name>/', MultiplayerConsumer.as_asgi()),
]


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_server.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)