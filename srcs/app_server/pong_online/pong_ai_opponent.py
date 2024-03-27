import random

W_WIDTH = 600
W_HEIGHT = 400

class AIPongOpponent:

	def __init__(self, paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight, dt, level):
		self.errorLevels = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0] #index 10 the hardest --> 0 error
		self.geometricPredictedY = 0
		self.dt = dt
		if level < 0:
			self.level = 0
		elif level > 10:
			self.level = 10
		else:
			self.level = level
		self.setGameState(paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight)

	def __predict_y_on_ai_paddleside(self):
		triangleHieght = (self.ballVelocityY/self.ballVelocityX) * (self.paddleX - self.ballX)
		if (self.ballVelocityY == 0):
			return self.ballY
		y_virtual_hit = self.ballY + triangleHieght
		if (y_virtual_hit < 0):
			y_virtual_hit *= -1
		if ((y_virtual_hit // W_HEIGHT) % 2 == 0):
			return y_virtual_hit % W_HEIGHT
		elif ((y_virtual_hit // W_HEIGHT) % 2 != 0):
			return W_HEIGHT - (y_virtual_hit % W_HEIGHT)
		
	def __moveInternalPaddle(self, aimedPosition):
		paddleCenterY = self.paddleY + self.paddleHeight / 2

		#move up to the aimed position if the paddle is below the aimed position
		if ((paddleCenterY > aimedPosition) and (self.paddleY > 0)):
			self.paddleY -= (self.paddleStepSize * self.dt)
			return -1
		#move down to the aimed position if the paddle is above the aimed position
		elif((paddleCenterY < aimedPosition) and (self.paddleY < W_HEIGHT - self.paddleHeight)):
			self.paddleY += (self.paddleStepSize * self.dt)
			return 1
		else:
			return 0
		
	def setGameState(self, paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight):
		self.paddleY = paddleY
		self.paddleX = paddleX
		self.paddleStepSize = paddleStepSize
		self.paddleHeight = paddleHeight
		self.ballX = ballX
		self.ballY = ballY
		self.ballVelocityX = ballVelocityX
		self.ballVelocityY = ballVelocityY
		randomFactor = random.choice((1, -1)) * random.random() #random float between -1.0 and +1.0
		errorFactor = random.uniform(0 , self.errorLevels[self.level])
		if self.paddleY > ballY:
			errorFactor *= -1
		self.geometricPredictedY = self.__predict_y_on_ai_paddleside() + (W_HEIGHT * errorFactor) + randomFactor * self.paddleHeight / 2


	def getAIDecision(self):
		screenCenterY = W_HEIGHT / 2
		#ball moves away from the ai paddle
		if (self.ballVelocityX < 0):
			return self.__moveInternalPaddle(aimedPosition=screenCenterY)
		#ball moves towards the ai paddle
		else:
			return self.__moveInternalPaddle(aimedPosition=self.geometricPredictedY)