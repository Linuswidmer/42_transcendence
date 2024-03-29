import pygame
import time
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

class Entity:
	def __init__(self, x, y, dx, dy) -> None:
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

class Ball(Entity):
	def __init__(self, x, y, dx, dy, radius, color) -> None:
		super().__init__(x, y, dx, dy)
		self.radius = radius
		self.color = color
		self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius,
							2 * self.radius, 2 * self.radius)
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

	def check_ball_paddle_collision(self, new_x, new_y, leftPaddle, rightPaddle):

		# if the ball is moving right (positive dx) the possible 
		# collision will be with the right paddle
		paddle = rightPaddle if self.dx > 0 else leftPaddle

		# Create a new rect for the ball's new position
		new_ball_rect = pygame.Rect(new_x, new_y, self.radius, self.radius)

		# Check if the new ball rect collides with the paddle's rect
		if new_ball_rect.colliderect(paddle.hitbox):
			# If the new x-position is within its radius of the left or right of the paddle,
			# it means the ball has hit the left or right of the paddle.
			# In this case, we reverse the x-direction of the ball to simulate a bounce.
			if abs(new_x - paddle.x) < self.radius or abs(new_x - (paddle.x + paddle.width)) < self.radius:
				self.dx *= -1
			else: # The ball hit the top or bottom of the paddle
				self.dy *= -1

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
			if self.dx > 0:
				leftPaddle.score += 1
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
	def __init__(self) -> None:
		self.leftPaddle = Paddle(0, SCREEN_HEIGHT / 2 - 70,
						0, 200, 15, 70, (255, 255, 255))
		self.rightPaddle = Paddle(SCREEN_WIDTH - 15, SCREEN_HEIGHT / 2 - 70,
						0, 200, 15, 70, (255, 255, 255))
		self.ball = Ball(0, 0,
						200, 200, 5, (255, 255, 255))
	
	


	
	def	update_entities(self, dt, game_data):
		player1_data, player2_data = list(game_data.values())
		player1_id, player2_id = list(game_data.keys())
		player1_direction = player1_data["direction"]
		player2_direction = player2_data["direction"]

		self.leftPaddle.move(dt, player1_direction)
		self.rightPaddle.move(dt, player2_direction)
		self.ball.move(dt, self.leftPaddle, self.rightPaddle)
		return {'ballX': self.ball.x, 'ballY': self.ball.y,
		  player1_id: {"x": self.leftPaddle.x, "y": self.leftPaddle.y, "score": self.leftPaddle.score},
		  player2_id: {"x": self.rightPaddle.x, "y": self.rightPaddle.y, "score": self.rightPaddle.score}}

def main():
	# Initialize Pygame
	pygame.init()

	# Create the display surface (canvas)
	canvas = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	# Create a Pong game
	pong = Pong()

	# Game loop
	running = True
	clock = pygame.time.Clock()  # Add a clock to control the frame rate

	topPaddle = pong.topPaddle
	bottomPaddle = pong.bottomPaddle
	ball = pong.ball

	def input_from_keyboard(topPaddle, bottomPaddle):
		running = True
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					topPaddle.isMoving = True
					topPaddle.direction = -1
				elif event.key == pygame.K_RIGHT:
					topPaddle.isMoving = True
					topPaddle.direction = 1
				elif event.key == pygame.K_a:
					bottomPaddle.isMoving = True
					bottomPaddle.direction = -1
				elif event.key == pygame.K_d:
					bottomPaddle.isMoving = True
					bottomPaddle.direction = 1
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					topPaddle.isMoving = False
				elif event.key == pygame.K_a or event.key == pygame.K_d:
					bottomPaddle.isMoving = False
		return running

	def visualize_game(canvas, topPaddle, bottomPaddle, ball):
		# Draw canvas
		canvas.fill((0, 0, 0))  # Clear the canvas with black

		# Draw paddles
		pygame.draw.rect(canvas, topPaddle.color, topPaddle.hitbox)  # Draw the paddle
		pygame.draw.rect(canvas, bottomPaddle.color, bottomPaddle.hitbox)

		# Draw ball
		pygame.draw.circle(canvas, ball.color, (ball.x, ball.y),
						ball.radius)

		# Update the display
		pygame.display.flip()




	while running:
		#this determines the tickrate that our server can send updated
		
		dt = clock.tick(60) / 1000  # Amount of seconds between each loop

		# Event handling for keyboard
		running = input_from_keyboard(topPaddle, bottomPaddle)

		# backend would usually receive keypresses via JSON
		# API for this need to be developed

		topPaddle.move(dt)  # Pass the input to the move function
		bottomPaddle.move(dt)  # Pass the input to the move function
		
		pong.check_ball_paddle_collision(dt)

		ball.move(dt)

		# develop API to send world state to client

		# visualize the game for development/debugging 
		visualize_game(canvas, topPaddle, bottomPaddle, ball)

		

	# Quit Pygame
	pygame.quit()

if __name__ == "__main__":
	main()