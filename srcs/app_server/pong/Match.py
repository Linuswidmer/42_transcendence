from pong_game import Pong

#a Match contains everything needed for a 2 player pong game
#
class Match:
	def __init__(self) -> None:
		self.pong_instance = Pong()
		self.paddles = {}