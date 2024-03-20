from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "first_name", "last_name",)

class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta(UserChangeForm):
        model = User
        fields = ("username", "email", "first_name", "last_name",)

class CustomProfileChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar',]