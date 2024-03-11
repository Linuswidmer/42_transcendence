import pygame
import random
import time
import math

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 225, 0)

# Define the paddle class
class Paddle:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.width = 10
		self.height = 100
		self.rect = pygame.Rect(x, y, self.width, self.height)
		self.speed = 5
		self.refresh_timer = time.time()

	def draw(self):
		pygame.draw.rect(WIN, WHITE, self.rect)

	def move_up(self):
		self.y -= self.speed
		self.rect.y = self.y

	def move_down(self):
		self.y += self.speed
		self.rect.y = self.y

# Define the ball class
class Ball:
	def __init__(self):
		self.reset()

	def reset(self):
		self.x = WIDTH // 2
		self.y = HEIGHT // 2
		self.size = 10
		self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
		self.speed_x = 4 * random.choice((1, -1))
		self.speed_y = 4 * random.choice((1, -1))

	def draw(self):
		pygame.draw.ellipse(WIN, WHITE, self.rect)

	def move(self):
		self.x += self.speed_x
		self.y += self.speed_y

		# Bounce off the top and bottom
		if self.y <= 0 or self.y >= HEIGHT - self.size:
			self.speed_y *= -1

		self.rect.x = self.x
		self.rect.y = self.y

	def bounce(self, player_paddle, ai_paddle):
		if self.rect.colliderect(player_paddle.rect):
			self.speed_x *= -1

			# Calculate the angle at which the ball hits the paddle
			relative_intersect_y = (player_paddle.rect.centery - self.rect.centery) / (player_paddle.rect.height / 2)
			bounce_angle = relative_intersect_y * (5 * math.pi / 12)  # Maximum angle for maximum bounce

			# Calculate the new speed components
			speed_magnitude = math.sqrt(self.speed_x ** 2 + self.speed_y ** 2)
			self.speed_x = speed_magnitude * math.cos(bounce_angle)
			self.speed_y = speed_magnitude * -math.sin(bounce_angle)

		if self.rect.colliderect(ai_paddle.rect):
			self.speed_x *= -1


def predict_y_on_ai_paddleside():
	kathete = (ball.speed_y/ball.speed_x) * (ai_paddle.x - ball.x)
	if (ball.speed_y == 0):
		return ball.y
	y_virtual_hit = ball.y + kathete #can be negative depending on speed_y --> is dann subtracted correctly
	if (y_virtual_hit < 0):
		y_virtual_hit *= -1
	if ((y_virtual_hit // HEIGHT) % 2 == 0):
		return y_virtual_hit % HEIGHT
	elif ((y_virtual_hit // HEIGHT) % 2 != 0):
		return HEIGHT - (y_virtual_hit % HEIGHT)

def predict_y_on_player_paddleside():
	kathete = (abs(ball.speed_y/ball.speed_x)) * (ball.x - player_paddle.x - (player_paddle.width))
	if (ball.speed_y == 0):
		return ball.y
	elif (ball.speed_y < 0):
		y_virtual_hit = ball.y - kathete
	else:
		y_virtual_hit = ball.y + kathete
	if (y_virtual_hit < 0):
		y_virtual_hit *= -1
	if ((y_virtual_hit // HEIGHT) % 2 == 0):
		return y_virtual_hit % HEIGHT
	elif ((y_virtual_hit // HEIGHT) % 2 != 0):
		return HEIGHT - (y_virtual_hit % HEIGHT)


# Create paddles and ball
player_paddle = Paddle(20, HEIGHT // 2 - 50)
ai_paddle = Paddle(WIDTH - 30, HEIGHT // 2 - 50)
ball = Ball()

# Game loop
clock = pygame.time.Clock()
running = True
ai_paddle.refresh_timer = time.time()
predicted_y_ai = predict_y_on_ai_paddleside()
predicted_y_player = predict_y_on_player_paddleside()
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	keys = pygame.key.get_pressed()
	if keys[pygame.K_w] and player_paddle.rect.y > 0:
		player_paddle.move_up()
	if keys[pygame.K_s] and player_paddle.rect.y < HEIGHT - player_paddle.height:
		player_paddle.move_down()
	
	

	# AI opponent
	if (time.time() - ai_paddle.refresh_timer >= 1):
		print("Recalculate...")
		predicted_y_ai = predict_y_on_ai_paddleside()
		predicted_y_player = predict_y_on_player_paddleside()
		ai_paddle.refresh_timer = time.time()
	if (ball.speed_x > 0):
		if ((ai_paddle.y + ai_paddle.height / 2 > predicted_y_ai) and (ai_paddle.y > 0)):
			ai_paddle.move_up()
		elif((ai_paddle.y + ai_paddle.height / 2 < predicted_y_ai) and (ai_paddle.y < HEIGHT - ai_paddle.height)):
			ai_paddle.move_down()
	else:
		if (ai_paddle.y + ai_paddle.height / 2 > HEIGHT / 2):
			ai_paddle.move_up()
		else:
			ai_paddle.move_down()

	# Move ball
	ball.move()
	ball.bounce(player_paddle, ai_paddle)

	# Check for scoring
	if ball.rect.x < 0 or ball.rect.x > WIDTH:
		ball.reset()

	# Draw everything
	WIN.fill(BLACK)
	if (ball.speed_x > 0):
		pygame.draw.rect(WIN, RED, (WIDTH - (WIDTH - ai_paddle.x) - ball.rect.width, predicted_y_ai, ball.rect.width, ball.rect.height))
	if (ball.speed_x < 0):
		pygame.draw.rect(WIN, YELLOW, (player_paddle.x + player_paddle.width, predicted_y_player, ball.rect.width, ball.rect.height))
	player_paddle.draw()
	ai_paddle.draw()
	ball.draw()
	pygame.draw.aaline(WIN, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT)) # Center line
	pygame.display.update()

	clock.tick(60)

pygame.quit()
