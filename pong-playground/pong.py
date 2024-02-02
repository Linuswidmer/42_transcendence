import pygame
import time

class Entity:
	def __init__(self, x, y, dx, dy) -> None:
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.start_time = 0
		self.direction = 0

class Paddle(Entity):
	def __init__(self, x, y, dx, dy, width, height, color) -> None:
		super().__init__(x, y, dx, dy)
		self.width = width
		self.height = height
		self.color = color
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)

	def update_pos(self, x: int):
		self.hitbox = pygame.Rect(x, self.y,self.width, self.height)

	def move(self, dt: int) -> None:
		self.update_pos(self.dx * dt * self.direction)

class Pong:
	def __init__(self) -> None:
		self.topPaddle = Paddle(400, 580, 200, 0, 70, 15, (255, 255, 255))

# Initialize Pygame
pygame.init()

# Create the display surface (canvas)
canvas = pygame.display.set_mode((800, 600))

# Create a Pong game
pong = Pong()

# Game loop
running = True
clock = pygame.time.Clock()  # Add a clock to control the frame rate
while running:
	dt = clock.tick(60) / 1000  # Amount of seconds between each loop
	# Event handling
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				pong.topPaddle.start_time = time.time()  # Record the current time
				pong.topPaddle.direction = -1  # Record the direction
			elif event.key == pygame.K_RIGHT:
				pong.topPaddle.start_time = time.time()  # Record the current time
				pong.topPaddle.direction = 1  # Record the direction
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
				elapsed_time = time.time() - pong.topPaddle.start_time  # Calculate the elapsed time

				pong.topPaddle.move(elapsed_time)  # Pass the input to the move function

	# Game logic
	# pong.topPaddle.move(dt)  # Update the paddle's position

	# Draw everything
	canvas.fill((0, 0, 0))  # Clear the canvas with black
	pygame.draw.rect(canvas, pong.topPaddle.color, pong.topPaddle.hitbox)  # Draw the paddle
	# Update the display
	pygame.display.flip()

# Quit Pygame
pygame.quit()