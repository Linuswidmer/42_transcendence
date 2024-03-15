class UserStatistics():
	def __init__(self, user_email):
		self.user_email = user_email
		#Game
		self.totalGames = 0 #
		self.totalGameTime = 0 #
		self.totalScoredPointsLocal = 0#
		self.totalScoredPointsRemote = 0#
		self.totalScoredPointsAI = 0#
		self.highestStrikeLocal = 0#
		self.highestStrikeRemote = 0#
		self.highestStrikeAI = 0#
		self.highestScoreLocal = 0#
		self.highestScoreRemote = 0#
		self.highestScoreAI = 0#
		self.longestBallRallyLocal = 0#
		self.longestBallRallyRemote = 0#
		self.longestBallRallyAI = 0#
		self.totalWins = 0#
		self.totalDefeats = 0#
		self.totalBallHits = 0#
		self.totalBallMisses = 0#
		#Tournament
		self.bestTournamentRank = 0
		self.totalTournamentsAttended = 0

	def calculateStats(self):
		self.__calcTounramentStats()
		self.__calcGameStats()

	"""
		Tournament section:
			- Total tournaments
			- pie diagram of total attended tournaments, won tournaments, lost tournament
			- best tournament rank
			—> List of all tournaments user attended
	"""
	def __calcTounramentStats(self):
		#get list of all tournament_ids of the user from the tournaments_user_junction table
		tournament_ids = TournamentUserJunction.objects.filter(user_email_fk=self.user_email).values_list('tournament_id_fk', flat=True)
		for id in tournament_ids:
			#get tournament rank

			#increment TournamentRank if 1st

			#if bestTournamentRank = 0 --> set Rank

			#elif Rank < bestTorunamentRank --> set Rank
			self.totalTournamentsAttended += 1


	"""
		Gameplay section:
			- Total games
			- Total game time
			—> List of all matches user attended

		Performance section:
			- bar chart: average points/game remote  (local, remote, AI)
			- bar chart: longest ball rally  (local, remote, AI)
			- pie Diagram of attempts, missed balls, hit balls
			- pie diagram of total games, wins, defeats
			- global ranking with win/lose ratio (remote)
			- bar chart: best game score  (local, remote, AI)
			- bar chart: highest winning strike (local, remote, AI)
	"""
	def __calcGameStats(self):
		#get list of all game_ids of the user from the games_user_junction table
		game_ids = GamesUserJunction.objects.filter(user_email_fk=self.user_email).values_list('games_id_fk', flat=True)
		for id in game_ids:
			self.totalGames += 1
			self.totalGameTime += game.gameDuration

			game = Games.objects.get(id=id)
			if game.winner == game.loser:
				pass
			elif game.winner == self.user_email:
				self.totalWins += 1
			else:
				self.totalDefeats += 1

			if self.user_email = game.initiatingPlayer:
				self.totalBallHits += game.ballHitsInitiatingPlayer
				self.totalBallMisses += game.ballMissesInitiatingPlayer
				if game.gameType == "local":
					self.totalScoredPointsLocal += game.scoreInitiatingPlayer
					if self.highestStrikeLocal < game.longestStreakInitiatingPlayer:
						self.highestStrikeLocal = game.longestStreakInitiatingPlayer
					if self.highestScoreLocal < game.scoreInitiatingPlayer:
						self.highestScoreLocal = game.scoreInitiatingPlayer
					if self.longestBallRallyLocal < game.longestBallRallyHits:
						self.longestBallRallyLocal = game.longestBallRallyHits
				if game.gameType == "remote":
					self.totalScoredPointsRemote += game.scoreInitiatingPlayer
					if self.highestStrikeRemote < game.longestStreakInitiatingPlayer:
						self.highestStrikeRemote = game.longestStreakInitiatingPlayer
					if self.highestScoreRemote < game.scoreInitiatingPlayer:
						self.highestScoreRemote = game.scoreInitiatingPlayer
					if self.longestBallRallyRemote < game.longestBallRallyHits:
						self.longestBallRallyRemote = game.longestBallRallyHits
				if game.gameType == "ai":
					self.totalScoredPointsAI += game.scoreInitiatingPlayer
					if self.highestStrikeAI < game.longestStreakInitiatingPlayer:
						self.highestStrikeAI = game.longestStreakInitiatingPlayer
					if self.highestScoreAI < game.scoreInitiatingPlayer:
						self.highestScoreAI = game.scoreInitiatingPlayer
					if self.longestBallRallyAI < game.longestBallRallyHits:
						self.longestBallRallyAI = game.longestBallRallyHits

			if self.user_email = game.acceptingPlayer:
				self.totalBallHits += game.ballHitsAcceptingPlayer
				self.totalBallMisses += game.ballMissesAcceptingPlayer
				if game.gameType == "local":
					self.totalScoredPointsLocal += game.scoreAcceptingPlayer
					if self.highestStrikeLocal < game.longestStreakAcceptingPlayer:
						self.highestStrikeLocal = game.longestStreakAcceptingPlayer
					if self.highestScoreLocal < game.scoreAcceptingPlayer:
						self.highestScoreLocal = game.scoreAcceptingPlayer
					if self.longestBallRallyLocal < game.longestBallRallyHits:
						self.longestBallRallyLocal = game.longestBallRallyHits
				if game.gameType == "remote":
					self.totalScoredPointsRemote += game.scoreAcceptingPlayer
					if self.highestStrikeRemote < game.longestStreakAcceptingPlayer:
						self.highestStrikeRemote = game.longestStreakAcceptingPlayer
					if self.highestScoreRemote < game.scoreAcceptingPlayer:
						self.highestScoreRemote = game.scoreAcceptingPlayer
					if self.longestBallRallyRemote < game.longestBallRallyHits:
						self.longestBallRallyRemote = game.longestBallRallyHits
				if game.gameType == "ai":
					self.totalScoredPointsAI += game.scoreAcceptingPlayer
					if self.highestStrikeAI < game.longestStreakAcceptingPlayer:
						self.highestStrikeAI = game.longestStreakAcceptingPlayer
					if self.highestScoreAI < game.scoreAcceptingPlayer:
						self.highestScoreAI = game.scoreAcceptingPlayer
					if self.longestBallRallyAI < game.longestBallRallyHits:
						self.longestBallRallyAI = game.longestBallRallyHits

			else:


"""
self.gameType = gameType
		self.gameStartTime = time.time() #
		self.gameDuration = 0 #calculated at the end
		self.matchDate = datetime.datetime.now().strftime("%Y-%m-%d") #
		self.matchTime = datetime.datetime.now().strftime("%H:%M:%S") #
		self.initiatingPlayer = initiatingPlayer #
		self.acceptingPlayer = acceptingPlayer #
		self.scoreInitiatingPlayer = 0 #
		self.scoreAcceptingPlayer = 0 #
		self.initiatingPlayerStrikeCtr = 0 #
		self.acceptingPlayerStrikeCtr = 0 #
		self.longestStreakInitiatingPlayer = 0 #
		self.longestStreakAcceptingPlayer = 0 #
		self.longestBallRallyHits = 0 #
		self.currentRallyHits = 0 #
		self.winner = "" #set at the end
		self.loser = "" #set at the end
		self.ballMissesTotal = 0 #set at the end
		self.ballMissesInitiatingPlayer = 0 #set at the end
		self.ballMissesAcceptingPlayer = 0 #set at the end
		self.ballHitsTotal = 0 #
		self.ballHitsInitiatingPlayer = 0 #
		self.ballHitsAcceptingPlayer = 0 #
		self.tournament_id = tournament_id
"""

