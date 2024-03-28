from django.db import models
from django.contrib.auth.models import User

class Tournaments(models.Model):
	pass

class Games(models.Model):
	matchName = models.CharField(max_length=200, default='')
	gameType = models.CharField(max_length=100, default='')
	gameDuration = models.IntegerField(default=0)
	matchDate = models.CharField(default='')
	matchTime = models.CharField(default='')
	tournament = models.ForeignKey(Tournaments, on_delete=models.CASCADE, null=True)

class UserGameStats(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	game = models.ForeignKey(Games, on_delete=models.CASCADE, null=True)
	score = models.IntegerField(default=0)
	ballHits = models.IntegerField(default=0)
	ballMisses = models.IntegerField(default=0)
	highestStreak = models.IntegerField(default=0)
	longestBallRallyHits = models.IntegerField(default=0)