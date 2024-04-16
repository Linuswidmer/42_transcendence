from django.contrib.auth import login, authenticate
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

def dashboard(request):
    return render(request, "userManagement/dashboard.html")

def my_view(request):
    if request.user.is_authenticated:
        return render(request, "onepager/logged_in.html")
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
            return redirect(reverse('userManagement:profile', args=[user.username]))
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
            return redirect("userManagement:profile_list")
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
            return redirect(reverse('userManagement:profile', args=[request.user.username]))
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
            return redirect(reverse('userManagement:profile', args=[request.user.username]))
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
            return redirect(reverse('userManagement:dashboard'))
        else:
            return render(
            request, "userManagement/register.html",
            {"form": form}
        )

def profile_list(request):
    #registered_user_group = Group.objects.get(name='registered_users')
    #registered_users = registered_user_group.user_set.all()
    all_users = User.objects.all()
    return render(request, "userManagement/profile_list.html", {"registered_users": all_users})

@login_required
def profile(request):
    user = get_object_or_404(User, username=request.user)
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(user.profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(user.profile)
        current_user_profile.save()
    return render(request, "userManagement/profile.html", {"user": user})

def logged_in(request):
    return render(request, 'onepager/logged_in.html')

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
