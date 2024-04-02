from django.urls import path
from .views import pong_online, display_lobby, register_player, join

app_name = "pong_online"

urlpatterns = [
    path("pong_online/", pong_online, name="pong_online"),
	path("lobby/", display_lobby, name="display_lobby"),
	path('register_player/', register_player, name='register_player'),
    path('join/', join, name='join'),
]
