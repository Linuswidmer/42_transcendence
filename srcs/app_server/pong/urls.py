from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/', views.game, name='game'),
    path('ws_test/', views.ws_test, name='ws_test'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path("sections/<str:name>", views.section, name='section'),
]
