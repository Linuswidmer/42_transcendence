from django.urls import re_path

from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/pong/$', consumers.PongConsumer.as_asgi()),
# ]

# from channels.routing import ChannelNameRouter, ProtocolTypeRouter, URLRouter
# from channels.sessions import SessionMiddlewareStack
# from django.conf.urls import url

# from consumers import GameConsumer, PlayerConsumer

# application = ProtocolTypeRouter(
#     {
#         "websocket": SessionMiddlewareStack(URLRouter([url(r"^ws/pong/$", PlayerConsumer)])),
#         "channel": ChannelNameRouter({"game_engine": GameConsumer}),
#     }
# )
