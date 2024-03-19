from .models import Games
from .models import UserGameStats
from .models import Tournaments
from django.contrib.auth.models import User

class StatsBuilder:
	def __init__(self, user):
		self.user = user
		self.totalTournaments = 0
		self.wonTournaments = 0
		self.bestTournamentRank = 0
		self.totalGames = 0 #
		self.totalGameTime = 0#
		self.averagePointsPerGameLocal = 0#
		self.averagePointsPerGameRemote = 0#
		self.averagePointsPerGameAI = 0#
		self.bestGameScoreLocal = 0#
		self.bestGameScoreRemote = 0#
		self.bestGameScoreAI = 0#
		self.longestBallRallyLocal = 0#
		self.longestBallRallyRemote = 0#
		self.longestBallRallyAI = 0#
		self.highestWinningStreakLocal = 0#
		self.highestWinningStreakRemote = 0#
		self.highestWinningStreakyAI = 0#
		self.totalMisses = 0#
		self.totalHits = 0#
		self.totalWins = 0#
		self.totalDefeats = 0#
		self.totalDraws = 0#

	def build(self):
		localGames = []
		remoteGames = []
		aiGames = []

		user_game_stats = UserGameStats.objects.filter(user=self.user)
		
		#iterate over all UserGameStats from the given user
		for stat in user_game_stats:
			if stat.game.gameType == 'local':
				localGames.append(stat.game)
			if stat.game.gameType == 'remote':
				remoteGames.append(stat.game)
			if stat.game.gameType == 'ai':
				aiGames.append(stat.game)
			self.totalGames += 1
			self.totalGameTime += stat.game.gameDuration
			self.totalHits += stat.ballHits
			self.totalMisses += stat.ballMisses

			opponent_score = UserGameStats.objects.filter(game=stat.game).exclude(user=self.user).first().score
			if opponent_score > stat.score:
				self.totalDefeats += 1
			elif opponent_score < stat.score:
				self.totalWins += 1
			else:
				self.totalDraws += 1
		
		for game in localGames:
			user_stat = UserGameStats.objects.filter(game=game).exclude(user=self.user).first()
			self.averagePointsPerGameLocal += user_stat.score
			if self.bestGameScoreLocal < user_stat.score:
					self.bestGameScoreLocal = user_stat.score
			if self.longestBallRallyLocal < user_stat.longestBallRallyHits:
				self.longestBallRallyLocal = user_stat.longestBallRallyHits
			if self.highestWinningStreakLocal < user_stat.highestStreak:
				self.highestWinningStreakLocal = user_stat.highestStreak
		self.averagePointsPerGameLocal = self.averagePointsPerGameLocal/localGames.count()

		for game in remoteGames:
			user_stat = UserGameStats.objects.filter(game=game).exclude(user=self.user).first()
			self.averagePointsPerGameRemote += user_stat.score
			if self.bestGameScoreRemote < user_stat.score:
					self.bestGameScoreRemote = user_stat.score
			if self.longestBallRallyRemote < user_stat.longestBallRallyHits:
				self.longestBallRallyRemote = user_stat.longestBallRallyHits
			if self.highestWinningStreakRemote < user_stat.highestStreak:
				self.highestWinningStreakRemote = user_stat.highestStreak
		self.averagePointsPerGameRemote = self.averagePointsPerGameRemote/remoteGames.count()#

		for game in aiGames:
			user_stat = UserGameStats.objects.filter(game=game).exclude(user=self.user).first()
			self.averagePointsPerGameAI += user_stat.score
			if self.bestGameScoreAI < user_stat.score:
					self.bestGameScoreAI = user_stat.score
			if self.longestBallRallyAI < user_stat.longestBallRallyHits:
				self.longestBallRallyAI = user_stat.longestBallRallyHits
			if self.highestWinningStreakAI < user_stat.highestStreak:
				self.highestWinningStreakAI = user_stat.highestStreak
		self.averagePointsPerGameAI = self.averagePointsPerGameAI/aiGames.count()



