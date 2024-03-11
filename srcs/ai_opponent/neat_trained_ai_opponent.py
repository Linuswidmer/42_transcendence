import pygame
from pong import Game
import neat
import os
import pickle
import time

class PongGame:
	def __init__(self, window, width, height):
			self.game = Game(window, width, height) #must be the dimension of our game
			self.left_paddle = self.game.left_paddle
			self.right_paddle = self.game.right_paddle
			self.ball = self.game.ball
	
	def play(self, genome, config):
		ai = neat.nn.FeedForwardNetwork.create(genome,config)

		run = True
		clock = pygame.time.Clock()
		start_time = time.time()
		output = ai.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
		decision = output.index(max(output))
		while run:
			clock.tick(60) #max 60 frames per second

			#react to the pressed Cross
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
					break

			keys = pygame.key.get_pressed()
			if keys[pygame.K_w]:
				self.game.move_paddle(left=True, up=True)
			if keys[pygame.K_s]:
				self.game.move_paddle(left=True, up=False)
			
			#if (time.time() - start_time >= 1):
			output = ai.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
			decision = output.index(max(output))
			start_time = time.time()

			if (decision == 0):
				pass
			elif (decision == 1):
				self.game.move_paddle(left=False, up=True)
			else:
				self.game.move_paddle(left=False, up=False)
			
			self.game.loop()
			self.game.draw()
			pygame.display.update()

		pygame.quit()

	def train_ai(self, genome1, genome2, config):
		#create two nural networs based on the genomes, which can take the current game state
		#as an input and move the paddle based on the output. We than evaluate the move and update 
		#the fitness value
		nn1 = neat.nn.FeedForwardNetwork.create(genome1, config)
		nn2 = neat.nn.FeedForwardNetwork.create(genome2, config)

		run = True
		while run:
			#react to the pressed Cross
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
			
			#trigger the network, get the 3 output values and get the greatest of these outputs. TBD: Why the greatest?
			output1 = nn1.activate((self.left_paddle.y, self.ball.y, abs(self.left_paddle.x - self.ball.x)))
			decision1 = output1.index(max(output1)) #TBD: why take the maximum value?

			#TBD: How comes this order?
			if (decision1 == 0):
				pass
			elif (decision1 == 1):
				self.game.move_paddle(left=True, up=True)
			else:
				self.game.move_paddle(left=True, up=False)
	
			output2 = nn2.activate((self.right_paddle.y, self.ball.y, abs(self.right_paddle.x - self.ball.x)))
			decision2 = output2.index(max(output2))

			if (decision2 == 0):
				pass
			elif (decision2 == 1):
				self.game.move_paddle(left=False, up=True)
			else:
				self.game.move_paddle(left=False, up=False)

			game_info = self.game.loop()
			self.game.draw(draw_score=False, draw_hits=True)
			pygame.display.update()

			#stop the ai training game as soon as one paddle missed a ball. This is just a approach to make the training
			# short. TBD: maybe think of an other method
			if (game_info.left_score >= 1 or game_info.right_score >= 1) or game_info.left_hits > 50:
				self.set_fitness(genome1, genome2, game_info)
				break

	def set_fitness(self, genome1, genome2, game_info):
		genome1.fitness += game_info.left_hits
		genome2.fitness += game_info.right_hits

#Train the AI:
#Play every genome against every other gonome and increase the fitness values when they hit
#genomes: list of tuples containing the genome-id and the genome itself
def eval_genomes(genomes, config):
	#create a new game for training
	window = pygame.display.set_mode((700, 500))

	#play each genome against any other genome but not itself 
	for i, (genome_id1, genome1) in enumerate(genomes):
		if (i == len(genomes) - 1):
			break
		#set the initial fitness of the current genome to 0
		genome1.fitness = 0
		for genome_id2, genome2 in genomes[i+1:]:
			#prevent a fitness value to be rest if it was already was set
			genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
			game = PongGame(window, 700, 500)
			game.train_ai(genome1, genome2, config) #TBD: Do we want this in the PongGame class


def run_neat_algorithm(config):
	#define the start population to start with as defined in the config
	p = neat.Population(config)

	#laod from a checkpoint
	#p = neat.Checkpointer.restore_checkpoint('name of checkpoint')

	#add reports about each generation to the std output
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	#creates a "Snapshot" after every 1 generations and safes it to a file
	#a generation can be started from a certain checkpoint
	p.add_reporter(neat.Checkpointer(1))

	#start the algorithm for max 50 iterations and a fitness function which
	# takes all genomes and set their fitness state based on their performance
	#Neat takes then the genomes with the best fitness values, merge the different 'good'
	#attributes and create a new populaltion based on that improved version and test the
	#new population again.After reaching the threshold (400) or 50 iterations save the best genome
	best = p.run(eval_genomes, 50)
	with open("best.pickle", "wb") as f:
		pickle.dump(best, f)

def test_ai(config):
	window = pygame.display.set_mode((700,500))

	with open("best.pickle", "rb") as f:
		ai = pickle.load(f)
	
	game = PongGame(window, 700, 500)
	game.play(ai, config)

if __name__ == "__main__":
	#load the neat configeration file for training
	#get the directory of this current file
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "neat_config.txt")
	
	#create a neat config object out of the config text file
	#TBD: understand this more
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
						neat.DefaultSpeciesSet, neat.DefaultStagnation,
						config_path)

	#uncomment for train the AI
	run_neat_algorithm(config)

	#test_ai(config)
