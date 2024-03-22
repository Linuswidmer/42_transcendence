import os
# from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# from routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app_server.settings")

django_asgi_app = get_asgi_application()

#leon: i think we dont need this here, feel free to uncomment again if smth stopped working
# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AllowedHostsOriginValidator(
#             AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
#         ),
#     }
# )