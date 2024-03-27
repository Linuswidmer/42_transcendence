from django.urls import path, include
from .views import dashboard, profile_list, profile, register, single_game_stats

app_name = "userManagement"

urlpatterns = [
	#path("", dashboard, name="dashboard"),
	path("accounts/", include("django.contrib.auth.urls")),
	path("dashboard/", dashboard, name="dashboard"),
	path("register/", register, name="register"),
	path("profile_list/", profile_list, name="profile_list"),
	path("profile/<int:pk>", profile, name="profile"),
	path("singleGameStats/", single_game_stats, name="single_game_stats")
]