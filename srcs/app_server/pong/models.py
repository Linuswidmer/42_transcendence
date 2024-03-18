from django.db import models

class Test(models.Model):
	test = models.TextField()

class Games(models.Model):
	gameType = models.TextField()
	gameDuration = models.IntegerField(default=0)
	matchDate = models.TextField()
	matchTime = models.TextField()
	initiatingPlayer = models.TextField(default=None)
	acceptingPlayer = models.TextField(default=None)
	scoreInitiatingPlayer = models.IntegerField(default=0)
	scoreAcceptingPlayer = models.IntegerField(default=0)
	longestStreakInitiatingPlayer = models.IntegerField(default=0)
	longestStreakAcceptingPlayer = models.IntegerField(default=0)
	longestBallRallyHits = models.IntegerField(default=0)
	winner = models.TextField(default=None)
	loser = models.TextField(default=None)
	ballMissesTotal = models.IntegerField(default=0)
	ballMissesInitiatingPlayer = models.IntegerField(default=0)
	ballMissesAcceptingPlayer = models.IntegerField(default=0)
	ballHitsTotal = models.IntegerField(default=0)
	ballHitsInitiatingPlayer = models.IntegerField(default=0)
	ballHitsAcceptingPlayer = models.IntegerField(default=0)
	tournament = models.ForeignKey('Tournaments', on_delete=models.CASCADE, null=True)

class Users(models.Model):
	email_pk = models.TextField(primary_key=True)
	inGameWith = models.ForeignKey('Users', on_delete=models.CASCADE, null=True)
	isOnline = models.BooleanField(default=False)
	isSearchingGame = models.BooleanField(default=False)
	name = models.TextField()

class Tournaments(models.Model):
	pass

class GamesUsersJunction(models.Model):
	user_email = models.ForeignKey('Users', on_delete=models.CASCADE, null=True)
	game = models.ForeignKey('Games', on_delete=models.CASCADE, null=True)

class TournamentUsersJunction(models.Model):
	tournament = models.ForeignKey('Tournaments', on_delete=models.CASCADE, null=True)
	user_email = models.ForeignKey('Users', on_delete=models.CASCADE, null=True)