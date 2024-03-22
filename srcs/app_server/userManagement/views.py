from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from .models import Profile
from django.urls import reverse
from userManagement.forms import CustomUserCreationForm, CustomUserChangeForm, CustomProfileChangeForm, CustomGuestCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
import uuid

def dashboard(request):
    return render(request, "userManagement/dashboard.html")

def register_user(request):
    if request.method == "GET":
        return render(
            request, "userManagement/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            registered_users = Group.objects.get(name='registered_users')
            user = form.save()
            user.groups.add(registered_users)
            user.save()
            login(request, user)
            return redirect(reverse('userManagement:profile', args=[user.profile.id]))
        else:
            return render(
            request, "userManagement/register.html",
            {"form": form}
        )

def register_guest(request):
    if request.method == "GET":
        return render(
            request, "userManagement/register.html",
            {"form": CustomGuestCreationForm}
        )
    elif request.method == "POST":
        form = CustomGuestCreationForm(request.POST)
        if form.is_valid():
            guest_users = Group.objects.get(name='guest_users')
            user = form.save()
            user.groups.add(guest_users)
            user.set_unusable_password()
            user.save()
            login(request, user)
            return redirect("userManagement:profile_list")
        else:
            return render(
            request, "userManagement/register.html",
            {"form": form}
        )

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
            return redirect(reverse('userManagement:profile', args=[user.id]))
        else:
            return render(
            request, "userManagement/register.html",
            {"form": form}
        )

def update_profile(request):
    if request.method == "GET":
        form = CustomProfileChangeForm(instance=request.user.profile)
        return render(
            request, "userManagement/register.html",
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
            return redirect(reverse('userManagement:profile', args=[request.user.id]))
        else:
            return render(
            request, "userManagement/register.html",
            {"form": form}
        )

def profile_list(request):
    registered_user_group = Group.objects.get(name='registered_users')
    registered_users = registered_user_group.user_set.all()
    return render(request, "userManagement/profile_list.html", {"registered_users": registered_users})

def profile(request, pk):
    
    profile = Profile.objects.get(pk=pk)
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    return render(request, "userManagement/profile.html", {"profile": profile})