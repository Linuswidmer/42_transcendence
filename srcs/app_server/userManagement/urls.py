from django.urls import path, include

from .views import dashboard, profile_list, profile, register_user, register_guest, update_user, update_profile, change_password, index, stranger, logged_in, navbar, check_login_status, navigation, dynamic_content, single_game_stats, tournament_stats, home, follow, callback



app_name = "userManagement"

urlpatterns = [
    path("", index, name='index'),
	path("pong_online/", index, name="pong_online"),
	path("lobby/", index, name="display_lobby"),
	path("singleGameStats/", index, name="single_game_stats"),
	path("tournament_stats/<str:tournament_id>/", index, name="tournament_stats"),
    path('profile/<str:username>/', index, name='profile'),
    path("profile_list/", index, name="profile_list"),
	path('callback', callback, name='callback'),
	path("fetch/profile_list/", profile_list, name="fetch_profile_list"),
	path('fetch/profile/<str:username>/', profile, name='fetch_profile'),
	path("fetch/singleGameStats/", single_game_stats, name="fetch_single_game_stats"),
	path("fetch/tournament_stats/<str:tournament_id>/", tournament_stats, name="fetch_tournament_stats"),

	path("accounts/", include("django.contrib.auth.urls")),
	path("dashboard/", dashboard, name="dashboard"),
	path("register_user/", register_user, name="register_user"),
	path("register_guest/", register_guest, name="register_guest"),
	path("update_user/", update_user, name="update_user"),
	path("update_profile/", update_profile, name="update_profile"),
	path("follow/<str:username>", follow, name="follow"),


	path("home/", home, name="home"),
    path("change_password/", change_password, name="change_password"),
    path('stranger/', stranger, name='stranger'),
    path('logged_in/', logged_in, name='logged_in'),
    path('includes/navbar/', navbar, name='navbar'),
    path('includes/navigation/', navigation, name='navigation'),
    path('check_login_status/', check_login_status, name='check_login_status'),

]