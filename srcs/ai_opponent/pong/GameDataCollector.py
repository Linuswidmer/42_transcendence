import time
import datetime
import psycopg2

class GameData:
	def __init__(self, initiatingPlayer, acceptingPlayer, gameType):
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

	def endGame(self):
		self.gameDuration = int(time.time() - self.gameStartTime)
		if self.scoreInitiatingPlayer < self.scoreAcceptingPlayer:
			self.winner = self.acceptingPlayer
			self.loser = self.initiatingPlayer
		elif self.scoreInitiatingPlayer > self.scoreAcceptingPlayer:
			self.loser = self.acceptingPlayer
			self.winner = self.initiatingPlayer
		else:
			self.winner = self.initiatingPlayer
			self.loser = self.initiatingPlayer

		self.ballMissesTotal = self.scoreAcceptingPlayer + self.scoreInitiatingPlayer
		self.ballMissesAcceptingPlayer = self.scoreInitiatingPlayer
		self.ballMissesInitiatingPlayer = self.scoreAcceptingPlayer

	def ballHit(self, initiatingPlayer=True):
		self.currentRallyHits += 1
		if self.currentRallyHits > self.longestBallRallyHits:
				self.longestBallRallyHits = self.currentRallyHits
		self.ballHitsTotal +=1
		if initiatingPlayer:
			self.ballHitsInitiatingPlayer += 1
		else:
			self.ballHitsAcceptingPlayer += 1
		

	def endRally(self, initiatingPlayerWon=True):
		self.currentRallyHits = 0
		if initiatingPlayerWon:
			self.acceptingPlayerStrikeCtr = 0
			self.initiatingPlayerStrikeCtr += 1
			if self.initiatingPlayerStrikeCtr > self.longestStreakInitiatingPlayer:
					self.longestStreakInitiatingPlayer = self.initiatingPlayerStrikeCtr
			self.scoreInitiatingPlayer += 1
		else:
			self.initiatingPlayerStrikeCtr = 0
			self.acceptingPlayerStrikeCtr += 1
			if self.acceptingPlayerStrikeCtr > self.longestStreakAcceptingPlayer:
					self.longestStreakAcceptingPlayer = self.acceptingPlayerStrikeCtr
			self.scoreAcceptingPlayer += 1
	
	def printData(self):
		print('-----------------------------------------')
		print('COLLECTED GAME DATA:\n')
		attributes = vars(self)
		for attribute, value in attributes.items():
			print(f"{attribute}: {value}")
		print('-----------------------------------------')
	
	def storeGameinDB(self):
		#This is the way to do it later
		"""
		game_data = DjangoGameData(
			gameType=self.gameType, 
			gameDuration=self.gameDuration, 
			matchDate=self.matchDate,
			matchTime=self.matchTime,
			initiatingPlayer=self.initiatingPlayer,
			acceptingPlayer=self.acceptingPlayer,
			scoreInitiatingPlayer=self.scoreInitiatingPlayer,
			scoreAcceptingPlayer=self.scoreAcceptingPlayer,
			longestStreakInitiatingPlayer=self.longestStreakInitiatingPlayer,
			longestStreakAcceptingPlayer=self.longestStreakAcceptingPlayer,
			longestBallRallyHits=self.longestBallRallyHits,
			winner=self.winner,
			loser=self.loser,
			ballMissesTotal=self.ballMissesTotal,
			ballMissesInitiatingPlayer=self.ballMissesInitiatingPlayer,
			ballMissesAcceptingPlayer=self.ballMissesAcceptingPlayer,
			ballHitsTotal=self.ballHitsTotal,
			ballHitsInitiatingPlayer=self.ballHitsInitiatingPlayer,
			ballHitsAcceptingPlayer=self.ballHitsAcceptingPlayer
		)

		# Save the instance to the database
		game_data.save()
		"""
		#JUST FOR TESTING
		# Connect to the PostgreSQL database
		conn = psycopg2.connect(
			dbname="postgres",
			user="pong_user",
			password="coucou",
			host="127.0.0.1",
			port="5432"
		)

		# Create a cursor object
		cursor = conn.cursor()

		# Insert data into the table
		cursor.execute("""
	INSERT INTO pong_djangogamedata (
		"gameType", "gameDuration", "matchDate", "matchTime", "initiatingPlayer", "acceptingPlayer",
		"scoreInitiatingPlayer", "scoreAcceptingPlayer", "longestStreakInitiatingPlayer",
		"longestStreakAcceptingPlayer", "longestBallRallyHits", "winner", "loser",
		"ballMissesTotal", "ballMissesInitiatingPlayer", "ballMissesAcceptingPlayer",
		"ballHitsTotal", "ballHitsInitiatingPlayer", "ballHitsAcceptingPlayer"
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
	self.gameType, self.gameDuration, self.matchDate, self.matchTime,
	self.initiatingPlayer, self.acceptingPlayer,
	self.scoreInitiatingPlayer, self.scoreAcceptingPlayer,
	self.longestStreakInitiatingPlayer, self.longestStreakAcceptingPlayer,
	self.longestBallRallyHits, self.winner, self.loser,
	self.ballMissesTotal, self.ballMissesInitiatingPlayer,
	self.ballMissesAcceptingPlayer, self.ballHitsTotal,
	self.ballHitsInitiatingPlayer, self.ballHitsAcceptingPlayer
))


		# Commit the transaction
		conn.commit()

		# Close the cursor and the connection
		cursor.close()
		conn.close()

	""" def updateUserStats(self):
		#Pseudocode for updating both users if there was a DjangoUser models in the models.py
		initiatingUser_DBinstance = DjangoUser.objects.get(pk=self.initiatingPlayer)
		acceptingPlayer_DBinstance = DjangoUser.objects.get(pk=self.acceptingPlayer)

		initiatingUser_DBinstance.inGameWith = -1
		acceptingPlayer_DBinstance.inGameWith = -1

		if (self.gameType == "local"):
			initiatingUser_DBinstance.totalScoredPointsLocal += self.scoreInitiatingPlayer
			if self.longestStreakInitiatingPlayer > initiatingUser_DBinstance.highestStrikeLocal:
				initiatingUser_DBinstance.highestStrikeLocal = self.longestStreakInitiatingPlayer
			if self.scoreInitiatingPlayer > initiatingUser_DBinstance.highestScoreLocal:
				initiatingUser_DBinstance.highestScoreLocal = self.scoreInitiatingPlayer
			
			if self.longestBallRallyHits > initiatingUser_DBinstance.longestBallRallyLocal:
				initiatingUser_DBinstance.longestBallRallyLocal = self.longestBallRallyHits
		
		if (self.gameType == "remote"):
			initiatingUser_DBinstance.totalScoredPointsRemote += self.scoreInitiatingPlayer
			if self.longestStreakInitiatingPlayer > initiatingUser_DBinstance.highestStrikeRemote:
				initiatingUser_DBinstance.highestStrikeRemote = self.longestStreakInitiatingPlayer
			if self.scoreInitiatingPlayer > initiatingUser_DBinstance.highestScoreRemote:
				initiatingUser_DBinstance.highestScoreRemote = self.scoreInitiatingPlayer
			
			if self.longestBallRallyHits > initiatingUser_DBinstance.longestBallRallyRemote:
				initiatingUser_DBinstance.longestBallRallyRemote = self.longestBallRallyHits
		
		if (self.gameType == "ai"):
			initiatingUser_DBinstance.totalScoredPointsAI += self.scoreInitiatingPlayer
			if self.longestStreakInitiatingPlayer > initiatingUser_DBinstance.highestStrikeAI:
				initiatingUser_DBinstance.highestStrikeAI = self.longestStreakInitiatingPlayer
			if self.scoreInitiatingPlayer > initiatingUser_DBinstance.highestScoreAI:
				initiatingUser_DBinstance.highestScoreAI = self.scoreInitiatingPlayer
			
			if self.longestBallRallyHits > initiatingUser_DBinstance.longestBallRallyAI:
				initiatingUser_DBinstance.longestBallRallyAI = self.longestBallRallyHits

		if (self.winner == self.loser):
			pass#Do nothing
		elif (self.winner == initiatingUser_DBinstance.id):
			initiatingUser_DBinstance.totalWins =+ 1
			acceptingPlayer_DBinstance.totalDefeats += 1
		elif (self.winner == acceptingPlayer_DBinstance.id):
			acceptingPlayer_DBinstance.totalWins =+ 1
			initiatingUser_DBinstance.totalDefeats += 1
		
		
		initiatingUser_DBinstance.totalBallHits += self.ballHitsInitiatingPlayer
		initiatingUser_DBinstance.totalBallMisses += self.ballMissesInitiatingPlayer
		acceptingPlayer_DBinstance.totalBallHits += self.ballHitsAcceptingPlayer
		acceptingPlayer_DBinstance.totalBallMisses += self.ballMissesAcceptingPlayer


		initiatingUser_DBinstance.bestTournamentRank # TBD?
		initiatingUser_DBinstance.totalGameTime += self.gameDuration
		acceptingPlayer_DBinstance.totalGameTime += self.gameDuration """