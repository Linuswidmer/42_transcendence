from typing import Set
from pong_online.models import Games
from pong_online.models import UserGameStats
from pong_online.models import Tournaments
from django.contrib.auth.models import User

class GameListData:
	def __init__(self, game, userGameStats, opponentGameStats) -> None:
		self.game = game
		self.userGameStats = userGameStats
		self.opponentGameStats = opponentGameStats
	
#private Helper class which stores data of game type (local, remote, ai) data
# because they exist for each game type in order to create the statistics.
# Used in a dictionary with the game type as key
class _GameTypeStats:
	def __init__(self) -> None:
		self.averagePointsPerGame = 0
		self.bestGameScore = 0
		self.longestBallRally = 0
		self.highestWinningStreak = 0
		self.games = []

#This class create and stores all the stats in a object for a given user
# for the game type dependent and game type independent stats
class StatsBuilder:
	def __init__(self, user):
		self.user = user
		
		#game type independenet data
		self.totalTournaments = 0
		self.wonTournaments = 0
		self.bestTournamentRank = 0
		self.totalGames = 0
		self.totalGameTime = 0
		self.totalMisses = 0
		self.totalHits = 0
		self.totalWins = 0
		self.totalDefeats = 0

		#game type dependent data
		self.gameTypeStats = {
			'local': _GameTypeStats(),
			'remote': _GameTypeStats(),
			'ai': _GameTypeStats()
		}

		self.gameListData = []

		self.tournaments = []

	#This helper method returns a tupel: first is winner, second is loser. Both the same, when draw.
	def _getWinnerLoser(self, game: Games):
		stats = UserGameStats.objects.filter(game_id=game.id).order_by('id')
		if stats[0].score > stats[1].score:
			return stats[0].user, stats[1].user
		elif stats[0].score < stats[1].score:
			return stats[1].user, stats[0].user
		return stats[0].user, stats[1].user #change later, draws not possible

	#This helper method goes through all tournaments and their games for the user
	# and set the best rank of the user in all these tournaments
	def _setBestTournamentRank(self, tournaments_set: Set[Tournaments]):
		#go through each tournament
		for tm in tournaments_set:
			games = Games.objects.filter(tournament_id=tm)
			#dictionary that has the users as key and the amount of their won gmaes as values
			playerWins = {}
			#go through every game of this tournament
			for game in games:
				winner, loser = self._getWinnerLoser(game)
				#set the loser in order to be visible in the dictinary
				if loser not in playerWins:
					playerWins[loser] = 0
				#if winner is already in dict --> increments
				if winner in playerWins:
						playerWins[winner] += 1
				#if winner is not in dict initialize with 1
				elif winner not in playerWins:
					playerWins[winner] = 1
			#create a sorted list of all wins of all users, with the highst amount of wins in the begining
			winList = sorted(playerWins.values(), reverse=True)
			#since we know the wins of our user, its rank is just the index of all sorted wins (+1)
			rank = winList.index(playerWins[self.user]) + 1
			#update the stats
			if rank == 1:
				self.wonTournaments += 1
			if self.bestTournamentRank == 0 or rank < self.bestTournamentRank:
				self.bestTournamentRank = rank


	def build(self):
		#get all game stats of the current user
		userGameStats = UserGameStats.objects.filter(user=self.user)
		
		#iterate over all UserGameStats from the given user
		for stat in userGameStats:
			self.totalGames += 1
			self.totalGameTime += stat.game.gameDuration
			self.totalHits += stat.ballHits
			self.totalMisses += stat.ballMisses

			if stat.game.tournament != None:
				self.tournaments.append(stat.game.tournament)
			
			#Get both stats from user and opponent and store it grouped in an object
			# for displaying later
			gamStats = UserGameStats.objects.filter(game_id=stat.game.id).order_by('id')
			if gamStats[0].user == self.user:
				self.gameListData.append(GameListData(stat.game, gamStats[0], gamStats[1]))
			else:
				self.gameListData.append(GameListData(stat.game, gamStats[1], gamStats[0]))

			winner, loser = self._getWinnerLoser(stat.game)
			if winner == self.user:
				self.totalWins += 1
			elif loser == self.user:
				self.totalDefeats += 1

			#work on the gameTypeStat instance in order tp update the right stats
			gameTypeStat = self.gameTypeStats[stat.game.gameType]
			gameTypeStat.games.append(stat.game)
			gameTypeStat.averagePointsPerGame += stat.score
			if gameTypeStat.bestGameScore < stat.score:
				gameTypeStat.bestGameScore = stat.score
			if gameTypeStat.longestBallRally < stat.longestBallRallyHits:
				gameTypeStat.longestBallRally = stat.longestBallRallyHits
			if gameTypeStat.highestWinningStreak < stat.highestStreak:
				gameTypeStat.highestWinningStreak = stat.highestStreak
		
		self.totalTournaments = len(set(self.tournaments))
		#since a user can have multiple games in a tournament, we make a set
		# so that every tournament only occurs on time
		self._setBestTournamentRank(set(self.tournaments))

		#since we used the averagePointsPErGame to Sum up all scores,
		# we now need to divide them through all the games of the gameType (remote, local, ai)
		for key, gameTypeStat in self.gameTypeStats.items():
			numGames = len(gameTypeStat.games)
			if numGames > 0:
				gameTypeStat.averagePointsPerGame /= len(gameTypeStat.games)
		print("Stats Builder Tournaments: ", self.tournaments)