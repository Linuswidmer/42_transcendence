from django.db import models

class Games(models.Model):
	gameType = models.TextField()
	gameDuration = models.IntegerField()
	matchDate = models.TextField()
	matchTime = models.TextField()
	initiatingPlayer = models.TextField(default=None)
	acceptingPlayer = models.TextField(default=None)
	scoreInitiatingPlayer = models.IntegerField()
	scoreAcceptingPlayer = models.IntegerField()
	longestStreakInitiatingPlayer = models.IntegerField()
	longestStreakAcceptingPlayer = models.IntegerField()
	longestBallRallyHits = models.IntegerField()
	winner = models.TextField()
	loser = models.TextField()
	ballMissesTotal = models.IntegerField()
	ballMissesInitiatingPlayer = models.IntegerField()
	ballMissesAcceptingPlayer = models.IntegerField()
	ballHitsTotal = models.IntegerField()
	ballHitsInitiatingPlayer = models.IntegerField()
	ballHitsAcceptingPlayer = models.IntegerField()
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