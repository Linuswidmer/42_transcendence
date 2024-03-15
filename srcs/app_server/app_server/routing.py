from django.urls import path
from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application  # Import get_asgi_application
from channels.auth import AuthMiddlewareStack

from pong.consumers import PongConsumer, GameConsumer

websocket_urlpatterns = [
    path('ws/pong/<room_name>/', PongConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
	"channel": ChannelNameRouter({"lobby": GameConsumer.as_asgi()}),
})

# application = ProtocolTypeRouter(
#     {
#         "websocket": SessionMiddlewareStack(URLRouter([url(r"^ws/game/$", PlayerConsumer)])),
#         "channel": ChannelNameRouter({"game_engine": GameConsumer}),
#     }
# )
