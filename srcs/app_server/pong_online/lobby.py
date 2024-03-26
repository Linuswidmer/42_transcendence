from uuid import uuid4
from adjectiveanimalnumber import generate

class Lobby:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Lobby, cls).__new__(cls, *args, **kwargs)
			cls._instance.matches = {}
			cls._instance.registered_players_total = []
		return cls._instance

	#return correct match instance to consumer
	def get_match_by_player_id(self, player_id):
		for match in self.matches.values():
			if player_id in match.registered_players:
				return match
		return None
	
	def get_all_matches(self):
		return {match_id: match.get_registered_players() for match_id, match in self.matches.items()}
	
	def register_player_match(self, username, match_id):
		match = self.get_match(match_id)
		if not match:
			return False, "match does not exist"
		elif username in self.registered_players_total:
			return False, "player already registered"
		elif not (match.register_player(username)):
			return False, "game full"
		self.registered_players_total.append(username)
		return True, ""
		
	
	def add_match(self, match_id) -> bool:
		if match_id in self.matches:
			return False, "match name already exists"
		self.matches[match_id] = Match(match_id)
		return True, ""

	def get_match(self, match_id):
		return self.matches.get(match_id)
	

	# 	#generate unique identifier for match_id
	# 	#will also be used for group communication
	# 	match_id = str(uuid4)
	# 	self.games[match_id] = Match(match_id) 

	# def remove_game(self, game_id):
	# 	if game_id in self.games:
	# 		del self.games[game_id]

	# def get_game(self, game_id):
	# 	return self.games.get(game_id)

	# def get_all_games(self):
	# 	return self.games
	
class Match:
	def __init__(self, match_id) -> None:
		#generate unique identifier for group communication
		self.group_name = match_id
		self.n_registered_players = 0
		self.match_full = False
		self.registered_players = []

	def	register_player(self, user_id) -> bool:
		if self.match_full:
			return False
		self.n_registered_players += 1
		self.registered_players.append(user_id)
		if self.n_registered_players == 2:
			self.match_full = True
		return True

	def	get_registered_players(self):
		return self.registered_players

	def	join_match(self, user_id) -> bool:
		if user_id in self.registered_players:
			pass

	
	# def	leave_match(self, user_id):
	# 	if user_id in self.registered_players:
	# 		self.n_registered_players -= 1
	# 		self.registered_players.discard(user_id)
			


