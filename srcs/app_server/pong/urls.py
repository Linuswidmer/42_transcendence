from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("sections/<str:name>", views.section, name='section'),
    path('create_local_tournament/', views.create_local_tournament, name='create_local_tournament'),
]