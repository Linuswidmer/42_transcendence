from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import Profile
from django.urls import reverse
from userManagement.forms import CustomUserCreationForm

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
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "userManagement/profile_list.html", {"profiles": profiles})

def profile(request, pk):
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()

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