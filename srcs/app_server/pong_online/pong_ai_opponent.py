import random

class AIPongOpponent:
	def __init__(self, pong_instance, dt, level):
		self.screen_height = pong_instance.screen_height
		self.screen_width = pong_instance.screen_width
		self.errorLevels = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0] #index 10 the hardest --> 0 error
		self.geometricPredictedY = 0
		self.dt = dt
		if level < 0:
			self.level = 0
		elif level > 10:
			self.level = 10
		else:
			self.level = level
		self.setGameState(pong_instance)

	def __predict_y_on_ai_paddleside(self):
		triangleHieght = (self.ballVelocityY/self.ballVelocityX) * (self.paddleX - self.ballX)
		if (self.ballVelocityY == 0):
			return self.ballY
		y_virtual_hit = self.ballY + triangleHieght
		if (y_virtual_hit < 0):
			y_virtual_hit *= -1
		if ((y_virtual_hit // self.screen_height) % 2 == 0):
			return y_virtual_hit % self.screen_height
		elif ((y_virtual_hit // self.screen_height) % 2 != 0):
			return self.screen_height - (y_virtual_hit % self.screen_height)

	def __moveInternalPaddle(self, aimedPosition):
		paddleCenterY = self.paddleY + self.paddleHeight / 2
		if (abs(paddleCenterY - aimedPosition) < self.paddleStepSize * self.dt):
			return 0
		elif ((paddleCenterY > aimedPosition) and (self.paddleY > 0)):
			self.paddleY -= (self.paddleStepSize * self.dt)
			return -1
		#move down to the aimed position if the paddle is above the aimed position
		elif((paddleCenterY < aimedPosition) and (self.paddleY < self.screen_height - self.paddleHeight)):
			self.paddleY += (self.paddleStepSize * self.dt)
			return 1

	#def setGameState(self, paddleY, paddleX, ballX, ballY, ballVelocityX, ballVelocityY, paddleStepSize, paddleHeight):
	def setGameState(self, pong_instance):
		self.paddleY = pong_instance.rightPaddle.y
		self.paddleX = pong_instance.rightPaddle.x
		self.paddleStepSize = pong_instance.rightPaddle.dy
		self.paddleHeight = pong_instance.rightPaddle.height
		self.ballX = pong_instance.ball.x
		self.ballY = pong_instance.ball.y
		self.ballVelocityX = pong_instance.ball.dx
		self.ballVelocityY = pong_instance.ball.dy
		randomFactor = random.choice((1, -1)) * random.random() #random float between -1.0 and +1.0
		errorFactor = random.uniform(0 , self.errorLevels[self.level])
		if self.paddleY > self.ballY:
			errorFactor *= -1
		self.geometricPredictedY = self.__predict_y_on_ai_paddleside() + (self.screen_height * errorFactor) + randomFactor * self.paddleHeight * 0.45

	def getAIDecision(self):
		screenCenterY = self.screen_height / 2
		#ball moves away from the ai paddle
		if (self.ballVelocityX < 0):
			return self.__moveInternalPaddle(aimedPosition=screenCenterY)
		#ball moves towards the ai paddle
		else:
			return self.__moveInternalPaddle(aimedPosition=self.geometricPredictedY)