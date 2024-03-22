#import neat
import os
import pickle
import random

W_WIDTH = 700
W_HEIGT = 500

class AIPongOpponent:
	"""
	def __createAIOpponent(self):
		local_dir = os.path.dirname(__file__)
		config_path = os.path.join(local_dir, "neat_config.txt")
		config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
							neat.DefaultSpeciesSet, neat.DefaultStagnation,
							config_path)

		with open("best.pickle", "rb") as f:
			genome = pickle.load(f)
		return (neat.nn.FeedForwardNetwork.create(genome,config))
		"""

	def __predict_y_on_ai_paddleside(self):
		triangleHieght = (self.ballVelocityY/self.ballVelocityX) * (self.paddleX - self.ballX)
		if (self.ballVelocityY == 0):
			return self.ballY
		y_virtual_hit = self.ballY + triangleHieght
		if (y_virtual_hit < 0):
			y_virtual_hit *= -1
		if ((y_virtual_hit // W_HEIGT) % 2 == 0):
			return y_virtual_hit % W_HEIGT
		elif ((y_virtual_hit // W_HEIGT) % 2 != 0):
			return W_HEIGT - (y_virtual_hit % W_HEIGT)

	def __init__(self, paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight, level):
		self.geometricPredictedY = 0
		self.paddleY = paddleY
		self.paddleX = paddleX
		self.paddleStepSize = paddleStepSize
		self.paddleHeight = paddleHeight
		self.ballX = ballX
		self.ballY = ballY
		self.ballVelocityX = ballVelocityX
		self.ballVelocityY = ballVelocityY
		# self.ai = self.__createAIOpponent()
		self.aiDecision = 0
		self.level = level
		if level < 0:
			self.level = 0
		if level > 10:
			self.level = 10
		self.errorLevels = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0] #index 10 the hardest --> 0 error



	def setGameState(self, paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight):
		self.paddleY = paddleY
		self.paddleX = paddleX
		self.paddleStepSize = paddleStepSize
		self.paddleHeight = paddleHeight
		self.ballX = ballX
		self.ballY = ballY
		self.ballVelocityX = ballVelocityX
		self.ballVelocityY = ballVelocityY
		"""
		if (self.ballVelocityX < 0):
			output = self.ai.activate(
				(self.paddleY, self.ballY, abs(self.paddleX - self.ballX)))
			self.aiDecision = output.index(max(output))
		"""
		#else:
		self.paddleX = paddleX
		self.paddleY = paddleY
		randomFactor = random.choice((1, -1)) * random.random() #random float between -1.0 and +1.0
		errorFactor = random.uniform(0 ,self.errorLevels[self.level])
		if self.paddleY > ballY:
			errorFactor *= -1
		self.geometricPredictedY = self.__predict_y_on_ai_paddleside() + (W_HEIGT * errorFactor) + randomFactor * self.paddleHeight / 2

	def getAIDecision(self):
		# if (self.ballVelocityX < 0):
		# 	if self.aiDecision == 0:
		# 		return "STAY"
		# 	elif self.aiDecision == 1:
		# 		return "UP"
		# 	else:
		# 		return "DOWN"
		if (self.ballVelocityX < 0):
			if (self.paddleY + self.paddleHeight / 2 > W_HEIGT / 2):
				self.paddleY  -= self.paddleStepSize
				return "UP"
			elif(self.paddleY + self.paddleHeight / 2 < W_HEIGT / 2):
				self.paddleY += self.paddleStepSize
				return "DOWN"
			else:
				return "STAY"
		else:
			if ((self.paddleY + self.paddleHeight / 2 > self.geometricPredictedY) and (self.paddleY > 0)):
				self.paddleY  -= self.paddleStepSize
				return "UP"
			elif((self.paddleY+ self.paddleHeight / 2 < self.geometricPredictedY) and (self.paddleY < W_HEIGT - self.paddleHeight)):
				self.paddleY += self.paddleStepSize
				return "DOWN"
			else:
				return "STAY"

