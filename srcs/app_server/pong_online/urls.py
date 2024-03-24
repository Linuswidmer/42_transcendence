from django.urls import path
from .views import pong_online

app_name = "pong_online"

urlpatterns = [
    path("pong_online/", pong_online, name="pong_online"),
]
