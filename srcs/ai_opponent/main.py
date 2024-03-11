import pygame
from pong import Game
import time
from pong_ai_opponent import AIPongOpponent
from GameDataCollector import GameData

window = pygame.display.set_mode((700,500))
game = Game(window, 700, 500)
gd = GameData("Alex", "AI-Ursula")

run = True
clock = pygame.time.Clock()
ai = AIPongOpponent(game.right_paddle.y, game.right_paddle.y, game.ball.x, game.ball.y, game.ball.x_vel, game.ball.y_vel, game.right_paddle.VEL, game.right_paddle.HEIGHT)
decision = ai.getAIDecision()
start_time = time.time()
while run:

	#react to the pressed Cross
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			break

	if (time.time() - start_time >= 1):
		ai.setGameState(game.right_paddle.y, game.right_paddle.x, game.ball.x, game.ball.y, game.ball.x_vel, game.ball.y_vel, game.right_paddle.VEL, game.right_paddle.HEIGHT)
		start_time = time.time()

	decision = ai.getAIDecision()
	if decision == "STAY":
		pass
	if decision == "DOWN":
		game.move_paddle(left=False, up=False)
	if decision == "UP":
		game.move_paddle(left=False, up=True)

	keys = pygame.key.get_pressed()
	if keys[pygame.K_w]:
		game.move_paddle(left=True, up=True)
	if keys[pygame.K_s]:
		game.move_paddle(left=True, up=False)

	game.loop()
	game.draw()
	pygame.display.update()

	clock.tick(60)

pygame.quit()
