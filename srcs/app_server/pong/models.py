from django.db import models

class Users(models.Model):
	email_pk = models.TextField(primary_key=True)
	inGameWith = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='opponent')
	isOnline = models.BooleanField(default=False)
	isSearchingGame = models.BooleanField(default=False)
	name = models.TextField()

class PlayerGameStats(models.Model):
	player = models.ForeignKey('Users', on_delete=models.CASCADE, null=True)
	score = models.IntegerField(default=0)
	ballHits = models.IntegerField(default=0)
	ballMisses = models.IntegerField(default=0)
	highestStreak = models.IntegerField(default=0)

class Games(models.Model):
	player1 = models.OneToOneField(PlayerGameStats, on_delete=models.CASCADE, related_name='game_stats_player1', null=True)
	player2 = models.OneToOneField(PlayerGameStats, on_delete=models.CASCADE, related_name='game_stats_player2', null=True)
	gameType = models.TextField()
	gameDuration = models.IntegerField(default=0)
	matchDate = models.DateField()  # Use DateField instead of TextField for dates
	matchTime = models.TimeField()  # Use TimeField instead of TextField for times
	longestBallRallyHits = models.IntegerField(default=0)
	winner = models.OneToOneField(Users, on_delete=models.SET_NULL, related_name='won_games', null=True)
	loser = models.OneToOneField(Users, on_delete=models.SET_NULL, related_name='lost_games', null=True)
	ballMissesTotal = models.IntegerField(default=0)
	ballHitsTotal = models.IntegerField(default=0)
	tournament = models.ForeignKey('Tournaments', on_delete=models.CASCADE, null=True)

class Tournaments(models.Model):
	pass