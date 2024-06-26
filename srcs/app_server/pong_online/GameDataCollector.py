import time
import datetime
from .models import Games
from .models import UserGameStats
from .models import Tournaments

class GameDataCollector:
	def __init__(self, left_player, right_player, matchName, type='', tournament=None):
		self.django_games = Games.objects.create(
			gameType = type,
			matchName = matchName,
			matchDate = datetime.datetime.now().strftime("%Y-%m-%d"),
			matchTime = datetime.datetime.now().strftime("%H:%M:%S")
		)
		if tournament != None:
				self.django_tournament = Tournaments.objects.get(
					tournament_id = tournament
				)
				self.django_games.tournament_id = self.django_tournament
		else:
			self.django_tournament = None

		self.django_userstats_1 = UserGameStats.objects.create(
			user_id = left_player.id,
			game_id = self.django_games.id
		)
		
		self.django_userstats_2 = UserGameStats.objects.create(
			user_id = right_player.id,
			game_id = self.django_games.id
		)

		self.gameStartTime = time.time()
		self.currentRallyHits = 0
		self.streakCtrLeftPlayer = 0
		self.streakCtrRightPlayer = 0

	def makeUserWin(self, left=True):
		if left:
			self.django_userstats_1.score = 3
			self.django_userstats_2.score = 0
		else:
			self.django_userstats_1.score = 0
			self.django_userstats_2.score = 3

	def endGame(self):
		#print("GameDataCollector: End Game")
		self.django_games.gameDuration = int(time.time() - self.gameStartTime)
		self.django_userstats_1.ballMisses = self.django_userstats_2.score
		self.django_userstats_2.ballMisses = self.django_userstats_1.score
		self.django_games.save()
		self.django_userstats_1.save()
		self.django_userstats_2.save()
		if self.django_tournament != None:
			self.django_tournament.save()

	def ballHit(self, left=True):
		self.currentRallyHits += 1
		if self.currentRallyHits > self.django_userstats_1.longestBallRallyHits:
				self.django_userstats_1.longestBallRallyHits = self.currentRallyHits
				self.django_userstats_2.longestBallRallyHits = self.currentRallyHits
		if left:
			#print("GameDataCollector: Paddle Hit Left")
			self.django_userstats_1.ballHits += 1
		else:
			#print("GameDataCollector: Paddle Hit Right")
			self.django_userstats_2.ballHits += 1


	def endRally(self, leftUserWon=True):
		self.currentRallyHits = 0
		if leftUserWon:
			#print("GameDataCollector: End Rally Left Won")
			self.streakCtrRightPlayer = 0
			self.streakCtrLeftPlayer += 1
			if self.streakCtrLeftPlayer > self.django_userstats_1.highestStreak:
					self.django_userstats_1.highestStreak = self.streakCtrLeftPlayer
			self.django_userstats_1.score += 1
		else:
			#print("GameDataCollector: End Rally Right Won")
			self.streakCtrLeftPlayer = 0
			self.streakCtrRightPlayer += 1
			if self.streakCtrRightPlayer > self.django_userstats_2.highestStreak:
					self.django_userstats_2.highestStreak = self.streakCtrRightPlayer
			self.django_userstats_2.score += 1
	
	#def #printData(self):
		#print('-----------------------------------------')
		#print('COLLECTED GAME DATA:\n')
		#print('Game:')
		#attributes = vars(self.django_games)
		#for attribute, value in attributes.items():
			#print(f"{attribute}: {value}")
		#print('\n Stats User 1:')
		#attributes = vars(self.django_userstats_1)
		#for attribute, value in attributes.items():
			#print(f"{attribute}: {value}")
			#print('\n Stats User 2:')
		#attributes = vars(self.django_userstats_2)
		#for attribute, value in attributes.items():
			#print(f"{attribute}: {value}")
		#print('-----------------------------------------')