from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import json
from django.template import TemplateDoesNotExist

def index(request):
    return render(request, 'pong/base.html')
def ws_test(request):
    return render(request, 'pong/ws_test.html')

def game(request):
    return render(request, 'pong/pong_game.html')

def landing_page(request):
    return render(request, 'pong/landing_page.html')

def logged_in(request):
    return render(request, 'pong/logged_in.html')

def stranger(request):
    return render(request, 'pong/stranger.html')

def home(request):
     return render(request, 'pong/home.html')

def section(request, name):
    try:
        return render(request, f'pong/{name}.html')
    except TemplateDoesNotExist:
        raise Http404("No such section")
    