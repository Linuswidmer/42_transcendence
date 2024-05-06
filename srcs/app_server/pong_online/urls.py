from django.urls import path
from .views import pong_online, lobby, display_tournaments
from userManagement.views import index

app_name = "pong_online"

urlpatterns = [
    path("fetch/pong_online/", pong_online, name="pong_online"),
	path("fetch/lobby/", lobby, name="lobby"),
	
	path('tournament/<str:tournament_id>/', index, name='display_tournaments'),
	path('fetch/tournament/<str:tournament_id>/', display_tournaments, name='fetch_display_tournaments')
]
