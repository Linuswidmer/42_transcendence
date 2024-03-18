from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name",) # "favorite_color",)

class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta(UserChangeForm):
        model = User
        fields = ("username", "email", "first_name", "last_name",)