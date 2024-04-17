from django.shortcuts import render, redirect
import json

from pong_online.lobby import Lobby, Match

def landing_test(request):
	return render(request, "pong_online/landing_test.html")

# Create your views here.
def pong_online(request):
	print("pong online view")
	return render(request, "pong_online/pong_game.html")

def display_lobby(request):
	return render(request, "pong_online/lobby.html", {"username": request.user.username})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def display_tournaments(request, tournament_id):
	lobby = Lobby()
	print('display ', tournament_id)
	tournament = lobby.get_tournament(tournament_id)
	return render(request, "pong_online/tournament.html", {"tournament": tournament})

@csrf_exempt
def register_player(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		match_id = data.get('match_id')

		if match_id is None:
			return JsonResponse({'status': 'error', 'error_message': 'No match_id provided'})

	# Register user for match
	lobby = Lobby()
	match = lobby.get_match(int(match_id))
	if not match:
		return JsonResponse({'status': 'error', 'error_message': 'match does not exist'})
	if not (match.register_player("SESSION ID HERE?")):
		return JsonResponse({'status': 'error', 'error_message': 'match full'})
	return JsonResponse({'status': 'success'})

@csrf_exempt
def join(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		match_id = data.get('match_id')

		if match_id is None:
			return JsonResponse({'status': 'error', 'error_message': 'No match_id provided'})
	# Join match
	lobby = Lobby()
	match = lobby.get_match(int(match_id))
	if "SESSION ID HERE?" not in  match.get_registered_players():
		return JsonResponse({'status': 'error', 'error_message': 'you are not registered to this game'})
	# return JsonResponse({'status': 'success'})
	
	return redirect('pong_online:pong_online')
