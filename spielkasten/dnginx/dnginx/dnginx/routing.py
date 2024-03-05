# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application  # Import get_asgi_application
# from channels.auth import AuthMiddlewareStack
# import pong.routing

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             pong.routing.websocket_urlpatterns  # Corrected import statement
#         )
#     ),
# })


from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application  # Import get_asgi_application
from channels.auth import AuthMiddlewareStack
import pong.consumers

websocket_urlpatterns = [
    path('ws/pong/', pong.consumers.WebSocketConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
