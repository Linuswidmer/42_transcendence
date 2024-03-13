from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import json
from .tournament import create_tournament_tree
from django.template import TemplateDoesNotExist

def index(request):
    return render(request, 'pong/base.html')

def section(request, name):
    try:
        return render(request, f'pong/{name}.html')
    except TemplateDoesNotExist:
        raise Http404("No such section")

def create_local_tournament(request):
    if request.method == 'POST':
        # Parse the JSON data sent from the frontend
        players_data = json.loads(request.body)

        # print the data
        print(players_data)

        tournament_tree = create_tournament_tree(list(players_data.values()))

        # Create the tournament scheme using the player information
        # tournament_data = {'message': 'Tournament created successfully', 'tournament_tree': tournament_tree}

        # return JsonResponse(tournament_data)
        return JsonResponse(tournament_tree, safe=False)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'})