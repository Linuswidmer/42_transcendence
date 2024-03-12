from django.db import models

class Person(models.Model):
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)

class DjangoGameData(models.Model):
	gameType = models.CharField(max_length=30, default="default")
	gameDuration = models.IntegerField(default=0)
	matchDate = models.CharField(max_length=30, default="default") 
	matchTime = models.CharField(max_length=30, default="default") 
	initiatingPlayer = models.CharField(max_length=30, default="default") 
	acceptingPlayer = models.CharField(max_length=30, default="default") 
	scoreInitiatingPlayer = models.IntegerField(default=0) 
	scoreAcceptingPlayer = models.IntegerField(default=0) 
	longestStreakInitiatingPlayer = models.IntegerField(default=0) 
	longestStreakAcceptingPlayer = models.IntegerField(default=0) 
	longestBallRallyHits = models.IntegerField(default=0) 
	winner = models.CharField(max_length=30, default="default") 
	loser = models.CharField(max_length=30, default="default") 
	ballMissesTotal = models.IntegerField(default=0) 
	ballMissesInitiatingPlayer = models.IntegerField(default=0) 
	ballMissesAcceptingPlayer = models.IntegerField(default=0) 
	ballHitsTotal = models.IntegerField(default=0) 
	ballHitsInitiatingPlayer = models.IntegerField(default=0) 
	ballHitsAcceptingPlayer = models.IntegerField(default=0) 