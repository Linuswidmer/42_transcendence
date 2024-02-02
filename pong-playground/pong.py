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

		self.update_pos(new_x, new_y)


class Paddle(Entity):
	def __init__(self, x, y, dx, dy, width, height, color) -> None:
		super().__init__(x, y, dx, dy)
		self.width = width
		self.height = height
		self.color = color
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)
		self.isMoving = False
		self.direction = 0

	def update_pos(self, x: int):
		self.x = x
		self.hitbox = pygame.Rect(self.x, self.y,self.width, self.height)

	def move(self, dt) -> None:
		if (self.isMoving):
			new_x = self.x + (self.dx * dt * self.direction)

	   		# Check if the new position would be outside the screen
			if new_x < 0:
				new_x = 0
			elif new_x + self.width > SCREEN_WIDTH:
				new_x = SCREEN_WIDTH - self.width

			self.update_pos(new_x)

class Pong:
	# change initial properties of entities here
	def __init__(self) -> None:
		self.topPaddle = Paddle(SCREEN_WIDTH / 2 - 70, 0,
						200, 0, 70, 15, (255, 255, 255))
		self.bottomPaddle = Paddle(SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT - 15,
						200, 0, 70, 15, (255, 255, 255))
		self.ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
				   		200, 200, 5, (255, 255, 255))
		
	def check_ball_paddle_collision(self, dt):
		ball = self.ball

		# if the ball is moving up (negative dy) the possible 
		# collision will be with the top paddle
		paddle = self.topPaddle if ball.dy < 0 else self.bottomPaddle

		# Check if the ball's hitbox collides with the paddle's hitbox
		if (ball.hitbox.colliderect(paddle.hitbox)):
			# If the ball's new y-position is within its radius of the top or bottom of the paddle,
   			# it means the ball has hit the top or bottom of the paddle.
			# In this case, we reverse the y-direction of the ball to simulate a bounce.
			if abs((ball.y + ball.dy * dt) - paddle.y) < ball.radius or abs((ball.y + ball.dy * dt) - (paddle.y + paddle.height)) < ball.radius:
		   		ball.dy *= -1
			else: # The ball hit the side of the paddle
				ball.dx *= -1
		
			# increase or decrease dx of the ball if the paddle is moving
			# the same/ or opposite direction respectively
			if (paddle.isMoving and paddle.direction == 1):
				ball.dx = ball.dx * (0.5 if ball.dx < 0 else 1.5)
			elif (paddle.isMoving and paddle.direction == -1):
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


while running:
	dt = clock.tick(60) / 1000  # Amount of seconds between each loop
	# Event handling
	running = input_from_keyboard(topPaddle, bottomPaddle)

	topPaddle.move(dt)  # Pass the input to the move function
	bottomPaddle.move(dt)  # Pass the input to the move function
	
	pong.check_ball_paddle_collision(dt)

	ball.move(dt)

	# Draw canvas
	canvas.fill((0, 0, 0))  # Clear the canvas with black

	# Draw paddles
	pygame.draw.rect(canvas, pong.topPaddle.color, pong.topPaddle.hitbox)  # Draw the paddle
	pygame.draw.rect(canvas, pong.bottomPaddle.color, pong.bottomPaddle.hitbox)

	# Draw ball
	pygame.draw.circle(canvas, pong.ball.color, (pong.ball.x, pong.ball.y),
					pong.ball.radius)

	# Update the display
	pygame.display.flip()

# Quit Pygame
pygame.quit()