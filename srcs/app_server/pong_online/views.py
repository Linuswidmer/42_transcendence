from django.shortcuts import render, redirect
import json

from django.contrib.auth.decorators import login_required

from pong_online.lobby import Lobby

# Create your views here.
@login_required(login_url='/home')
def pong_online(request):
	#print("pong online view")
	return render(request, "pong_online/pong_game.html", {"username": request.user.username})

@login_required(login_url='/home')
def lobby(request):
	return render(request, "pong_online/lobby.html", {"username": request.user.username})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/home')
def display_tournaments(request, tournament_id):
	lobby = Lobby()
	#print('display ', tournament_id)
	tournament = lobby.get_tournament(tournament_id)
	return render(request, "pong_online/tournament.html", {"tournament": tournament}, {"username": request.user.username})