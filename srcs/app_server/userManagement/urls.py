from django.urls import path, include
from .views import dashboard, profile_list, profile, register_user, register_guest, update_user, update_profile, change_password, single_game_stats

app_name = "userManagement"

urlpatterns = [
	path("accounts/", include("django.contrib.auth.urls")),
	path("dashboard/", dashboard, name="dashboard"),
	path("register_user/", register_user, name="register_user"),
	path("register_guest/", register_guest, name="register_guest"),
	path("update_user/", update_user, name="update_user"),
	path("update_profile/", update_profile, name="update_profile"),
	path("profile_list/", profile_list, name="profile_list"),
    path('profile/<str:username>/', profile, name='profile'),
    path("change_password/", change_password, name="change_password"),

	path("singleGameStats/", single_game_stats, name="single_game_stats")
]