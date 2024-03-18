from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(
        "self", #pointing to profile
        related_name="followed_by", #field, that allows to acces data from otherhand of that relationship
        symmetrical=False, #you can follow without being followed back and vice versa
        blank=True #follows can be empty
    )
    def __str__(self):
        return self.user.username

# Creates a Profile for each new user automatically
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.add(instance.profile)
        user_profile.save()
