from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application  # Import get_asgi_application
from channels.auth import AuthMiddlewareStack

from pong.consumers import WebSocketConsumer, PongConsumer
from pong_online.consumers import MultiplayerConsumer

websocket_urlpatterns = [
    path('ws/pong/', WebSocketConsumer.as_asgi()),
    path('ws/pong/game/', PongConsumer.as_asgi()),
	path('ws/pong_online/game/', MultiplayerConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})