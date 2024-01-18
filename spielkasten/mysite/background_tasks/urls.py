# initialize the urls for the background_tasks app

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]