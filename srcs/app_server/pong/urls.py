from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_local_tournament/', views.create_local_tournament, name='create_local_tournament'),
]