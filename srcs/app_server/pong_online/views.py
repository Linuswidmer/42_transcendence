from django.shortcuts import render

# Create your views here.
def pong_online(request):
    return render(request, "pong_online/pong_game.html")
