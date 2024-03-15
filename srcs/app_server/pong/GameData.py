import time
import datetime
from models import Games

class GameData:
	def __init__(self, initiatingPlayer, acceptingPlayer, gameType, tournament_id=-1):
		self.games_instance = Games() #instance of the django model
		self.gameStartTime = time.time()
		self.currentRallyHits = 0
		self.acceptingPlayerStrikeCtr = 0
		self.initiatingPlayerStrikeCtr = 0
		self.games_instance.gameType = gameType
		self.games_instance.matchDate = datetime.datetime.now().strftime("%Y-%m-%d") #
		self.games_instance.matchTime = datetime.datetime.now().strftime("%H:%M:%S") #
		self.games_instance.initiatingPlayer = initiatingPlayer
		self.games_instance.acceptingPlayer = acceptingPlayer
		self.games_instance.tournament = tournament_id


	def endGame(self):
		self.games_instance.gameDuration = int(time.time() - self.gameStartTime)
		if self.games_instance.scoreInitiatingPlayer < self.games_instance.scoreAcceptingPlayer:
			self.games_instance.winner = self.games_instance.acceptingPlayer
			self.games_instance.loser = self.games_instance.initiatingPlayer
		elif self.games_instance.scoreInitiatingPlayer > self.games_instance.scoreAcceptingPlayer:
			self.games_instance.loser = self.games_instance.acceptingPlayer
			self.games_instance.winner = self.games_instance.initiatingPlayer
		else:
			self.games_instance.winner = self.games_instance.initiatingPlayer
			self.games_instance.loser = self.games_instance.initiatingPlayer

		self.games_instance.ballMissesTotal = self.games_instance.scoreAcceptingPlayer + self.games_instance.scoreInitiatingPlayer
		self.games_instance.ballMissesAcceptingPlayer = self.games_instance.scoreInitiatingPlayer
		self.games_instance.ballMissesInitiatingPlayer = self.games_instance.scoreAcceptingPlayer

		self.games_instance.save()

	def ballHit(self, initiatingPlayer=True):
		self.currentRallyHits += 1
		if self.currentRallyHits > self.games_instance.longestBallRallyHits:
				self.games_instance.longestBallRallyHits = self.currentRallyHits
		self.games_instance.ballHitsTotal +=1
		if initiatingPlayer:
			self.games_instance.ballHitsInitiatingPlayer += 1
		else:
			self.games_instance.ballHitsAcceptingPlayer += 1
		

	def endRally(self, initiatingPlayerWon=True):
		self.currentRallyHits = 0
		if initiatingPlayerWon:
			self.acceptingPlayerStrikeCtr = 0
			self.initiatingPlayerStrikeCtr += 1
			if self.initiatingPlayerStrikeCtr > self.games_instance.longestStreakInitiatingPlayer:
					self.games_instance.longestStreakInitiatingPlayer = self.initiatingPlayerStrikeCtr
			self.games_instance.scoreInitiatingPlayer += 1
		else:
			self.initiatingPlayerStrikeCtr = 0
			self.acceptingPlayerStrikeCtr += 1
			if self.acceptingPlayerStrikeCtr > self.games_instance.longestStreakAcceptingPlayer:
					self.games_instance.longestStreakAcceptingPlayer = self.acceptingPlayerStrikeCtr
			self.games_instance.scoreAcceptingPlayer += 1
	
	def printData(self):
		print('-----------------------------------------')
		print('COLLECTED GAME DATA:\n')
		attributes = vars(self)
		for attribute, value in attributes.items():
			print(f"{attribute}: {value}")
		print('-----------------------------------------')