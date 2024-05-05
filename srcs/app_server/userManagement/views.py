from django.contrib.auth import login, logout, authenticate, update_session_auth_hash, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from .models import Profile
from django.urls import reverse
from userManagement.forms import CustomUserCreationForm, CustomUserChangeForm, CustomProfileChangeForm, CustomGuestCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
import uuid
from .StatsBuilder import StatsBuilder, GameListData
from pong_online.models import UserGameStats, Tournaments, Games
import json
import requests
from django.contrib import messages
from django.shortcuts import redirect

def dashboard(request):
	return render(request, "userManagement/dashboard.html")

def index(request, username=None, tournament_id=None, match_id=None):
	return render(request, "onepager/index.html")

def	home(request):
	if request.user.is_authenticated:
		return render(request, "pong_online/lobby.html", {"username": request.user.username})
	else:
		return render(request, "onepager/stranger.html")

#view for registering a new user
def register_user(request):
	if request.method == "GET":
		return render(
			request, "userManagement/register.html",
			{"form": CustomUserCreationForm}
		)
	elif request.method == "POST":
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			registered_users, created = Group.objects.get_or_create(name='registered_users')
			user = form.save()
			user.groups.add(registered_users)
			user.save()
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			return redirect('userManagement:profile', {"username": user.username})
		else:
			return render(
			request, "userManagement/register.html",
			{"form": form}
		)

#view for registering a new guest
def register_guest(request):
	if request.method == "GET":
		return render(
			request, "userManagement/register.html",
			{"form": CustomGuestCreationForm}
		)
	elif request.method == "POST":
		form = CustomGuestCreationForm(request.POST)
		if form.is_valid():
			guest_users, created = Group.objects.get_or_create(name='guest_users')
			user = form.save()
			user.groups.add(guest_users)
			user.set_unusable_password()
			user.save()
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			return redirect("userManagement:logged_in")
		else:
			return render(
			request, "userManagement/register.html",
			{"form": form}
		)

#view for updating existing user
def update_user(request):
	if request.method == "GET":
		form = CustomUserChangeForm(instance=request.user)
		return render(
			request, "userManagement/register.html",
			{"form": form}
		)
	elif request.method == "POST":
		form = CustomUserChangeForm(request.POST, instance=request.user)
		if form.is_valid():
			user = form.save()
			return redirect('userManagement:profile', username=user.username)
		else:
			return render(
			request, "userManagement/register.html",
			{"form": form}
		)

#view for changing profile picture
def update_profile(request):
	if request.method == "GET":
		form = CustomProfileChangeForm(instance=request.user.profile)
		return render(
			request, "userManagement/update_profile.html",
			{"form": form}
		)
	elif request.method == "POST":
		current_avatar = request.user.profile.avatar
		#delete the current avatar if there is a new one
		if current_avatar and request.FILES and str(current_avatar) != "profile_images/default.jpg":
			avatar_path = os.path.join(settings.MEDIA_ROOT, str(current_avatar))
			if os.path.exists(avatar_path):
				os.remove(avatar_path)
		form = CustomProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
		if form.is_valid():
			form.save()
			return redirect('userManagement:profile', username=request.user.username)
		else:
			return render(
			request, "userManagement/update_profile.html",
			{"form": form}
		)

def change_password(request):
	if request.method == "GET":
		form = PasswordChangeForm(instance=request.user)
		return render(
			request, "userManagement/register.html",
			{"form": form}
		)
	elif request.method == "POST":
		form = PasswordChangeForm(request.POST, instance=request.user)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			return redirect('userManagement:profile', username=request.user.username)
		else:
			return render(
			request, "userManagement/register.html",
			{"form": form}
		)

def profile_list(request):
	all_users = User.objects.exclude(username="DUMP_LOCAL")
	return render(request, "userManagement/profile_list.html", {"registered_users": all_users})

@login_required(login_url='/home')
def profile(request, username):
	user = get_object_or_404(User, username=username)
	sb = StatsBuilder(user)
	sb.build()
	return render(request, "userManagement/profile.html", {"user": user, "stats": sb})

def follow(request, username):
	user = get_object_or_404(User, username=username)
	if request.method == "POST":
		#user = get_object_or_404(User, username=username)
		current_user_profile = request.user.profile
		data = request.POST
		action = data.get("follow")
		if action == "follow":
			current_user_profile.follows.add(user.profile)
		elif action == "unfollow":
			current_user_profile.follows.remove(user.profile)
		current_user_profile.save()
		return redirect('userManagement:profile', username=username)

def logged_in(request):
	return render(request, 'onepager/logged_in.html', {"username": request.user.username})

def stranger(request):
	return render(request, 'onepager/stranger.html')

def check_login_status(request):
	if request.user.is_authenticated:
		return JsonResponse({'logged_in': True})
	else:
		return JsonResponse({'logged_in': False})

def dynamic_content(request):
	# Your logic to fetch dynamic content
	data = {'message': 'This is dynamic content!'}
	return JsonResponse(data)


def navbar(request):
	return render(request, 'includes/navbar.html')

def navigation(request):
	return render(request, 'includes/navigation.html')

@login_required(login_url='/home')
def single_game_stats(request, match_id):
	game = Games.objects.get(matchName=match_id)
	user_game_stat = UserGameStats.objects.filter(game=game).first()
	user = user_game_stat.user
	sb = StatsBuilder(user)
	sb.build()
	for gld in sb.gameListData:
		if gld.game.matchName == match_id:
			return render(request, "userManagement/single_game_stats.html", {"gld": gld})

@login_required(login_url='/home')
def tournament_stats(request, tournament_id):
	tournament = Tournaments.objects.get(tournament_id=tournament_id)
	return render(request, "userManagement/tournament_stats.html", {"tm_name": tournament.tournament_id, "tm_data": json.dumps(tournament.data)})


def callback(request):
	User = get_user_model()
	code = request.GET.get('code')
	if code:
		data = {
			'grant_type': 'authorization_code',
			'client_id': os.environ.get("OAUTH_CLIENT_ID"),
			'client_secret': os.environ.get("OAUTH_CLIENT_SECRET"),
			'code': code,
			'redirect_uri': os.environ.get("OAUTH_CALLBACK_URL"),
		}
		print(data)
		try:
			response = requests.post('https://api.intra.42.fr/oauth/token', data=data)
			response_data = response.json()
			print(response_data)
			access_token = response_data['access_token']
			user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': f'Bearer {access_token}'})
			user_info = user_info_response.json()
			# print(user_info)

			username = user_info['login']
			email = user_info['email']
			avatar_url = user_info['image']['link']
			last_name = user_info['last_name']
			first_name = user_info['first_name']
			#password = user_info['login'] + "@secretpw1#"
			user = User.objects.filter(username=username).first()
			if user:
				login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				user.online = True
				user.save()
				return redirect('/')
			else:
				# If the user doesn't exist, create a new user and log in
				user = User.objects.create_user(username=username, email=email, password=None)  # No password required
				user.first_name = first_name
				user.last_name = last_name
				user.avatar_url = avatar_url
				user.save()
				login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				user.online = True
				user.save()
				return redirect('/')
		except requests.exceptions.RequestException as e:
			print("Request Exception:", e)
			message = 'Failed to authenticate user. Please try again.'
			messages.error(request, message)
			return render(request, "onepage.html")
	else:
		message = 'Failed to reach API. Please try again.'
		messages.error(request, message)
		return render(request, "onepagr.html")
