from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.db.models.signals import pre_delete
from django.utils import timezone
from django.conf import settings
import os

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(
        "self", #pointing to profile
        related_name="followed_by", #field, that allows to acces data from otherhand of that relationship
        symmetrical=False, #you can follow without being followed back and vice versa
        blank=True #follows can be empty
    )
    #last_activity = models.DateTimeField(auto_now=True)
    logged_in = models.BooleanField(default=False)
    avatar = models.ImageField(default='profile_images/default.jpg', upload_to='profile_images')
   
    def __str__(self):
        return self.user.username

# Creates a Profile for each new user automatically
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

@receiver(user_logged_in)
def log_user_in(sender, request, user, **kwargs):
    user.profile.logged_in = True
    user.profile.save()

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    user.profile.logged_in = False
    user.profile.save()

@receiver(pre_delete, sender=User)
def pre_delete_user(sender, instance, **kwargs):
    current_avatar = instance.profile.avatar
    if current_avatar and str(current_avatar) != "profile_images/default.jpg":
        avatar_path = os.path.join(settings.MEDIA_ROOT, str(current_avatar))
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
