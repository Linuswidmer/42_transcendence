from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.urls import reverse
from userManagement.forms import CustomUserCreationForm
from .StatsBuilder import StatsBuilder, GameListData
from pong_online.models import UserGameStats


def dashboard(request):
	return render(request, "userManagement/dashboard.html")

def register(request):
	if request.method == "GET":
		return render(
			request, "userManagement/register.html",
			{"form": CustomUserCreationForm}
		)
	elif request.method == "POST":
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect(reverse('userManagement:profile', args=[user.profile.id]))


def profile_list(request):
	profiles = Profile.objects.all()
	return render(request, "userManagement/profile_list.html", {"profiles": profiles})

def profile(request, pk):
	if not hasattr(request.user, 'profile'):
		missing_profile = Profile(user=request.user)
		missing_profile.save()

	profile = Profile.objects.get(pk=pk)
	sb = StatsBuilder(profile.user)
	sb.build()
	if request.method == "POST":
		current_user_profile = request.user.profile
		data = request.POST
		action = data.get("follow")
		if action == "follow":
			current_user_profile.follows.add(profile)
		elif action == "unfollow":
			current_user_profile.follows.remove(profile)
		current_user_profile.save()
	return render(request, "userManagement/profile.html", {"profile": profile, "stats": sb})

def single_game_stats(request):
	game_id = int(request.GET.get('gameID'))
	user_id = int(request.GET.get('userID'))
	user = User.objects.get(id=user_id)
	sb = StatsBuilder(user)
	sb.build()
	for gld in sb.gameListData:
		if gld.game.id == game_id:
			return render(request, "userManagement/single_game_stats.html", {"gld": gld})