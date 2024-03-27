from django.urls import path
from . import views

app_name = 'pong'

urlpatterns = [
    path('', views.index, name='index'),
    path('', views.landing_page, name='landing_page'),
    path('game/', views.game, name='game'),
    path('ws_test/', views.ws_test, name='ws_test'),
   path("sections/<str:name>", views.section, name='section'),
]