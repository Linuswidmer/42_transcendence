from django.urls import path, include

from .views import dashboard, profile_list, profile, register_user, register_guest, update_user, update_profile, change_password, my_view, stranger, logged_in, navbar, check_login_status, navigation, dynamic_content, single_game_stats



app_name = "userManagement"

urlpatterns = [
	path("accounts/", include("django.contrib.auth.urls")),
	path("dashboard/", dashboard, name="dashboard"),
	path("register_user/", register_user, name="register_user"),
	path("register_guest/", register_guest, name="register_guest"),
	path("update_user/", update_user, name="update_user"),
	path("update_profile/", update_profile, name="update_profile"),

    path("profile_list/", profile_list, name="profile_list"),
    path('profile/', profile, name='profile'),

    path('profile/<str:username>/', profile, name='profile'),
    path("land/", my_view, name='my_view'),
    path("change_password/", change_password, name="change_password"),
    path('stranger/', stranger, name='stranger'),
    path('logged_in/', logged_in, name='logged_in'),
    path('includes/navbar/', navbar, name='navbar'),
    path('includes/navigation/', navigation, name='navigation'),
    path('check_login_status/', check_login_status, name='check_login_status'),

	path("singleGameStats/", single_game_stats, name="single_game_stats")
]