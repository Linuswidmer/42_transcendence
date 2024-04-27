from django.urls import path
from .views import pong_online, lobby, register_player, join, display_tournaments

app_name = "pong_online"

urlpatterns = [
    path("fetch_pong_online/", pong_online, name="pong_online"),
	path("fetch_lobby/", lobby, name="lobby"),
	
	
	path('register_player/', register_player, name='register_player'),
    path('join/', join, name='join'),
	path('tournament/<str:tournament_id>/', display_tournaments, name='display_tournaments')
]
