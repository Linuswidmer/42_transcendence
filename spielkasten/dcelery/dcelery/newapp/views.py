from django.shortcuts import render
from .tasks import sharedtask
from django.http import HttpResponse


def index(request):
    print('request to index!')

    sharedtask.delay()
    return render(request, 'newapp/index.html')


# Create your views here.
