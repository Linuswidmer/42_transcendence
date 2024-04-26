import pygame
import time
import random
import math
from asgiref.sync import sync_to_async, async_to_sync
import asyncio


############## CONSTANTS ###############
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 70
PADDLE_DY = 400

BALL_DX = 20
BALL_DY = 20
BALL_RADIUS = 10

MAX_BOUNCE_ANGLE = math.radians(50) #75 degree in radian
MAX_VELOCITY = 600
VELOCITY_INCREMENT = 30

WINNING_SCORE = 3

class Entity:
	def __init__(self, x, y, dx, dy) -> None:
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

class Ball(Entity):
	def __init__(self, x, y, dx, dy, radius, color, gameDataCollector) -> None:
		super().__init__(x, y, dx, dy)
		self.gameDataCollector = gameDataCollector
		self.radius = radius
		self.color = color
		self.tempMaxDy = BALL_DY
		self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius,
							2 * self.radius, 2 * self.radius)
		self.last_collided_paddle = None
		self.random_spawn()
	
	def update_pos(self, x: int, y: int):
		self.x = x
		self.y = y
		self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius,
							2 * self.radius, 2 * self.radius)

	def random_spawn(self):
		self.dx = random.choice([-1, 1]) * (self.dx + random.uniform(-0.5, 0.5))
		self.dy = random.choice([-1, 1]) * (self.dy + random.uniform(-0.5, 0.5))
		self.update_pos(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

	def move(self, dt: int, leftPaddle, rightPaddle) -> None:
		#calculate theoretical position of ball for next timestep
		new_x = self.x + (self.dx * dt)
		new_y = self.y + (self.dy * dt)

		#adjust dx,dy in case there is a collision
		self.check_ball_paddle_collision(new_x, new_y, leftPaddle, rightPaddle)
		self.check_ball_sidewalls_collision(new_x, new_y, leftPaddle, rightPaddle)
		
		#calculate the actual position with adjusted dx, dy
		new_x = self.x + (self.dx * dt)
		new_y = self.y + (self.dy * dt)

		self.update_pos(new_x, new_y)

	def update_velocity(self, velocity):
		if (velocity < MAX_VELOCITY):
			velocity += 20
		if (velocity > MAX_VELOCITY):
			velocity = MAX_VELOCITY
		return velocity

	def top_or_bottom_paddle_hit(self, paddle, ball_rect):
		intersection_rect = ball_rect.clip(paddle.hitbox)
		#print("Intersecting collision rect: ", intersection_rect)

		#since we are in the colliderect we have a collsion. If the intersect_rect
		# is higher, this means there is more vertical overlap, so we have a hit on
		# on the side. If heigth and witdh are eqal we rather want a side hit to keep
		# the game running
		if (intersection_rect.height >= intersection_rect.width):
			return "SIDE"
		elif (intersection_rect.height < intersection_rect.width):
			return "TOP_OR_BOTTOM"
		else:
			return "NONE"

	def check_ball_paddle_collision(self, new_x, new_y, leftPaddle, rightPaddle):

		# if the ball is moving right (positive dx) the possible 
		# collision will be with the right paddle
		paddle = rightPaddle if self.dx > 0 else leftPaddle

		# Create a new rect for the ball's new position
		new_ball_rect = pygame.Rect(new_x - self.radius, new_y - self.radius, 2 * self.radius, 2 * self.radius)

		# Check if the new ball rect collides with the paddle's rect
		if new_ball_rect.colliderect(paddle.hitbox):
			#prevent the colliderect function being called multiple times for one hit
			if (paddle == self.last_collided_paddle):
				return
			self.last_collided_paddle = paddle

			if self.gameDataCollector != None:
				if paddle == rightPaddle:
					self.gameDataCollector.ballHit(left=False)
				else:
					self.gameDataCollector.ballHit(left=True)
			# If the new x-position is within its radius of the left or right of the paddle,
			# it means the ball has hit the left or right of the paddle.
			# In this case, we reverse the x-direction of the ball to simulate a bounce.
			bounce = self.top_or_bottom_paddle_hit(paddle, new_ball_rect)
			if bounce == "SIDE":
				#print("SIDE HIT")
				initialYDirection = -1 if self.dy < 0 else 1
				newXDirection = -1 if self.dx > 0 else 1
				relativeIntersectToPaddleCenter = (paddle.y + (paddle.height / 2)) - self.y
				normalized = abs(relativeIntersectToPaddleCenter / (paddle.height / 2))
				bouncAngle = normalized * MAX_BOUNCE_ANGLE
				currentVel = math.sqrt(self.dx ** 2 + self.dy ** 2) + VELOCITY_INCREMENT
				if (currentVel > MAX_VELOCITY):
					currentVel = MAX_VELOCITY
				self.dx = currentVel * math.cos(bouncAngle) * newXDirection
				self.dy = currentVel * math.sin(bouncAngle) * initialYDirection

			elif bounce == "TOP_OR_BOTTOM" : # The ball hit the top or bottom of the paddle
				#print("TOP OR BOTTOM")
				self.dy *= -1

			else:
				print("NO HIT: Something went wrong")

			# increase or decrease dy of the ball if the paddle is moving
			# the same/ or opposite direction respectively
			if (paddle.direction == 1):
				self.dy = self.dy * (0.8 if self.dy < 0 else 1.2)
			elif (paddle.direction == -1):
				self.dy = self.dy * (0.8 if self.dy > 0 else 1.2)


	def check_ball_sidewalls_collision(self, new_x, new_y, leftPaddle, rightPaddle):
		# If the ball is at the left or right boundary, reverse its x direction
		if new_x - self.radius < 0 or new_x + self.radius > SCREEN_WIDTH:
			if self.dx < 0: #left side wall hit -> point for right player
				rightPaddle.score += 1
				if self.gameDataCollector != None:
					self.gameDataCollector.endRally(leftUserWon=False)
			if self.dx > 0:
				leftPaddle.score += 1
				if self.gameDataCollector != None:
					self.gameDataCollector.endRally(leftUserWon=True)
			self.tempMaxDy = BALL_DY
			self.dy = BALL_DY
			self.dx = BALL_DX
			self.last_collided_paddle = None
			self.random_spawn()
			return

		# If the ball is at the top or bottom boundary, reverse its y direction
		if new_y - self.radius < 0 or new_y + self.radius > SCREEN_HEIGHT:
			self.dy *= -1

class Paddle(Entity):
	def __init__(self, x, y, dx, dy, width, height, color) -> None:
		super().__init__(x, y, dx, dy)
		self.width = width
		self.height = height
		self.color = color
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)
		self.score = 0
		self.direction = 0

	def update_pos(self, y: int):
		self.y = y
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)

	def move(self, dt, direction) -> None:
		self.direction = direction
		if (direction):
			new_y = self.y + (self.dy * dt * direction)

			# Check if the new position would be outside the screen
			if new_y < 0:
				new_y = 0
			elif new_y + self.height > SCREEN_HEIGHT:
				new_y = SCREEN_HEIGHT - self.height

			self.update_pos(new_y)

class Pong:
	# change initial properties of entities here
	def __init__(self, gameDataCollector=None) -> None:
		self.leftPaddle = Paddle(0, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT,
						0, PADDLE_DY, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
		self.rightPaddle = Paddle(SCREEN_WIDTH - PADDLE_WIDTH, SCREEN_HEIGHT / 2 - PADDLE_HEIGHT,
						0, PADDLE_DY, PADDLE_WIDTH, PADDLE_HEIGHT, (255, 255, 255))
		self.ball = Ball(0, 0,
						BALL_DX, BALL_DY, BALL_RADIUS, (255, 255, 255), gameDataCollector)
		self.game_over = False
		self.gameDataCollector = gameDataCollector
		self.screen_width = SCREEN_WIDTH
		self.screen_height = SCREEN_HEIGHT
	
	def get_initial_entity_data(self, game_data):
		print(game_data)
		player1_id, player2_id = list(game_data.keys())
		print("Player IDs: ", player1_id, player2_id)
		return {'entities': {
					  'ball': {
						  'entity_type': 'ball',
						  'relX': self.ball.x / SCREEN_WIDTH,
						  'relY': self.ball.y / SCREEN_HEIGHT,
						  'relBallRadius': BALL_RADIUS / SCREEN_HEIGHT,
					  },
					  player2_id: {
						  'entity_type': 'paddle',
						  'screen_pos': 'left',
						  'relX': self.leftPaddle.x / SCREEN_WIDTH,
						  'relY': self.leftPaddle.y / SCREEN_HEIGHT,
						  'relPaddleHeight': PADDLE_HEIGHT / SCREEN_HEIGHT,
						  'relPaddleWidth': PADDLE_WIDTH / SCREEN_WIDTH,
						  "score": self.leftPaddle.score,
					  },
					  player1_id: {
						  'entity_type': 'paddle',
						  'screen_pos': 'right',
						  'relX': self.rightPaddle.x / SCREEN_WIDTH,
						  'relY': self.rightPaddle.y / SCREEN_HEIGHT,
						  'relPaddleHeight': PADDLE_HEIGHT / SCREEN_HEIGHT,
						  'relPaddleWidth': PADDLE_WIDTH / SCREEN_WIDTH,
						  "score": self.rightPaddle.score,
					  },
				},
		}

	async def	update_entities(self, dt, game_data, players):
		player1_id = players[0]
		player2_id = players[1]
		player1_data = game_data[player1_id]
		player2_data = game_data[player2_id]
		player1_direction = player1_data["direction"]
		player2_direction = player2_data["direction"]
		player1_score = player1_data["score"]
		player2_score = player2_data["score"]

		self.leftPaddle.move(dt, player2_direction)
		self.rightPaddle.move(dt, player1_direction)
		self.ball.move(dt, self.leftPaddle, self.rightPaddle)

		#the score is set to 3 in the consumer if one user closed the windwo during the game
		#so we use this information here to end the game and set the scores
		if (player1_score == WINNING_SCORE):
			if self.gameDataCollector != None:
				self.gameDataCollector.makeUserWin(left=False)
			self.leftPaddle.score = WINNING_SCORE
		if (player2_score == WINNING_SCORE):
			if self.gameDataCollector != None:
				self.gameDataCollector.makeUserWin(left=True)
			self.rightPaddle.score = WINNING_SCORE

		if (self.rightPaddle.score == WINNING_SCORE or self.leftPaddle.score == WINNING_SCORE):
			self.game_over = True
			if self.gameDataCollector != None:
				await sync_to_async(self.gameDataCollector.endGame)()
		return {'game_over': self.game_over,
		  		'entities': {
					  'ball': {
						  'relX': self.ball.x / SCREEN_WIDTH,
						  'relY': self.ball.y / SCREEN_HEIGHT,
					  },
					  player2_id: {
						  'relX': self.leftPaddle.x / SCREEN_WIDTH,
						  'relY': self.leftPaddle.y / SCREEN_HEIGHT,
						  "score": self.leftPaddle.score,
					  },
					  player1_id: {
						  'relX': self.rightPaddle.x / SCREEN_WIDTH,
						  'relY': self.rightPaddle.y / SCREEN_HEIGHT,
						  "score": self.rightPaddle.score,
					  },
				},
				'timestamp': int(time.time() * 1000),
				}


def visualize_game(canvas, leftPaddle, rightPaddle, ball):
	# Draw canvas
	canvas.fill((0, 0, 0))  # Clear the canvas with black

	# Draw paddles
	pygame.draw.rect(canvas, leftPaddle.color, leftPaddle.hitbox)  # Draw the paddle
	pygame.draw.rect(canvas, rightPaddle.color, rightPaddle.hitbox)

	# Draw ball
	pygame.draw.rect(canvas, (255, 0, 255), ball.hitbox)
	pygame.draw.circle(canvas, ball.color, (ball.x, ball.y),
					ball.radius)

	# Update the display
	pygame.display.flip()


def input_from_keyboard(gameData):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return False, None
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				gameData["playerRight"]["moveUp"] = True
			elif event.key == pygame.K_RIGHT:
				gameData["playerRight"]["moveDown"] = True
			elif event.key == pygame.K_a:
				gameData["playerLeft"]["moveUp"] = True
			elif event.key == pygame.K_d:
				gameData["playerLeft"]["moveDown"] = True
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
				gameData["playerRight"]["moveUp"] = False
				gameData["playerRight"]["moveDown"] = False
			elif event.key == pygame.K_a or event.key == pygame.K_d:
				gameData["playerLeft"]["moveUp"] = False
				gameData["playerLeft"]["moveDown"] = False
	
	if gameData["playerLeft"]["moveUp"] and not gameData["playerLeft"]["moveDown"]:
		gameData["playerLeft"]["direction"] = -1
	elif gameData["playerLeft"]["moveDown"] and not gameData["playerLeft"]["moveUp"]:
		gameData["playerLeft"]["direction"] = 1
	else:
		gameData["playerLeft"]["direction"] = 0

	if gameData["playerRight"]["moveUp"] and not gameData["playerRight"]["moveDown"]:
		gameData["playerRight"]["direction"] = -1
	elif gameData["playerRight"]["moveDown"] and not gameData["playerRight"]["moveUp"]:
		gameData["playerRight"]["direction"] = 1
	else:
		gameData["playerRight"]["direction"] = 0

	return True, gameData

def main():
	pygame.init()

# 	# Create the display surface (canvas)
	canvas = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	pong_instance = Pong()
	FPS = 60
	clock = pygame.time.Clock()  # Add a clock to control the frame rate
	iteration_time = 1 / FPS
	should_run = True
	players = ["playerRight", "playerLeft"]
	game_data = {
		"playerLeft": {
			"score": 0,
			"moveUp": False,
			"moveDown": False,
			"direction": 0
		},
		"playerRight": {
			"score": 0,
			"moveUp": False,
			"moveDown": False,
			"direction": 0
		}
	}
	while should_run:
		dt = clock.tick(60) / 1000  # Amount of seconds between each loop
		#update entities with the iteration_time and keypresses
		should_run, game_data = input_from_keyboard(gameData=game_data)
		if not should_run:
			break
		visualize_game(canvas, pong_instance.leftPaddle, pong_instance.rightPaddle, pong_instance.ball)
		entity_data = async_to_sync(pong_instance.update_entities)(dt, game_data, players)
		# entity_data = asyncio.run(async_wrapper(pong_instance, dt, game_data))
		should_run = not entity_data["game_over"]
		#send all entity data to clients, so they can render the game
		# print(entity_data)

if __name__ == "__main__":
	main()