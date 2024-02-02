import pygame
import time

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
	
	def update_pos(self, x: int, y: int):
		self.x = x
		self.y = y
		self.hitbox = pygame.Rect(self.x - self.radius, self.y - self.radius,
							2 * self.radius, 2 * self.radius)

	def move(self, dt: int) -> None:
		new_x = self.x + (self.dx * dt)
		new_y = self.y + (self.dy * dt)

		# If the ball is at the left or right boundary, reverse its x direction
		if new_x - self.radius < 0 or new_x + self.radius > SCREEN_WIDTH:
			self.dx *= -1

		# If the ball is at the top or bottom boundary, reverse its y direction
		if new_y - self.radius < 0 or new_y + self.radius > SCREEN_HEIGHT:
			self.dy *= -1

		self.update_pos(self.x + (self.dx * dt), self.y + (self.dy * dt))


class Paddle(Entity):
	def __init__(self, x, y, dx, dy, width, height, color) -> None:
		super().__init__(x, y, dx, dy)
		self.width = width
		self.height = height
		self.color = color
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)

	def update_pos(self, x: int):
		self.x = x
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)

	def move(self, dt) -> None:
		self.update_pos(self.x + (self.dx * dt))

class Pong:
	def __init__(self) -> None:
		self.topPaddle = Paddle(400, 580, 200, 0, 70, 15, (255, 255, 255))
		self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
				   200, 200, 5, (255, 255, 255))
		
	def check_ball_paddle_collision(self, dt, moveTop, directionTop):
		ball = self.ball
		topPaddle = self.topPaddle

		if (ball.hitbox.colliderect(topPaddle.hitbox)):
			if abs((ball.y + ball.dy*dt) - topPaddle.y) < ball.radius or abs((ball.y + ball.dy*dt) - (topPaddle.y + topPaddle.height)) < ball.radius:
		   		ball.dy *= -1
			else: # The ball hit the side of the paddle
				ball.dx *= -1
		
			if (moveTop and directionTop == 1):
				ball.dx = ball.dx * (0.5 if ball.dx < 0 else 1.5)
			elif (moveTop and directionTop == -1):
				ball.dx = ball.dx * (0.5 if ball.dx > 0 else 1.5)

# Initialize Pygame
pygame.init()

# Create the display surface (canvas)
canvas = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a Pong game
pong = Pong()

# Game loop
running = True
clock = pygame.time.Clock()  # Add a clock to control the frame rate
moveTop = False
direction = 0

while running:
	dt = clock.tick(60) / 1000  # Amount of seconds between each loop
	# Event handling
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				moveTop = True
				direction = -1  # Record the direction
			elif event.key == pygame.K_RIGHT:
				moveTop = True
				direction = 1  # Record the direction
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
				moveTop = False

	if (moveTop):
		pong.topPaddle.move(dt * direction)  # Pass the input to the move function
	pong.check_ball_paddle_collision(dt, moveTop, direction)
	pong.ball.move(dt)

	# Draw everything
	canvas.fill((0, 0, 0))  # Clear the canvas with black
	pygame.draw.rect(canvas, pong.topPaddle.color, pong.topPaddle.hitbox)  # Draw the paddle

	pygame.draw.circle(canvas, pong.ball.color, (pong.ball.x, pong.ball.y),
					pong.ball.radius)

	# Update the display
	pygame.display.flip()

# Quit Pygame
pygame.quit()