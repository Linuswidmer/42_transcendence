from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import json
from django.template import TemplateDoesNotExist
from django.contrib.auth.views import LoginView
from django.urls import reverse

def index(request):
    return render(request, 'pong/base.html')
def ws_test(request):
    return render(request, 'pong/ws_test.html')

def game(request):
    return render(request, 'pong/pong_game.html')

#def section(request, name):
#    try:
#        return render(request, f'pong/{name}.html')
#    except TemplateDoesNotExist:
#        raise Http404("No such section")
def landing_page(request):
    return render(request, 'pong/landing_page.html')

def section(request, name):
    if name == "login":
        return HttpResponse(status=302, headers={'Location': reverse('userManagement:login')})
    elif name == "login42":
        html_content = render(request, 'provider:complete_login')
    elif name == "register":
       html_content = render(request, 'userManagement:register_user')
    else:
        # Return a 404 response if the section is not found
        return HttpResponse(status=404)
    
    return HttpResponse(html_content)