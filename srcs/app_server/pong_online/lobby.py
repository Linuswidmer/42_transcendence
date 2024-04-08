from uuid import uuid4
from adjectiveanimalnumber import generate
import copy

class Lobby:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Lobby, cls).__new__(cls, *args, **kwargs)
			cls._instance.matches = {}
			cls._instance.registered_players_total = []
			nameMatch1 = "1"
			cls._instance.add_match(nameMatch1)
			match1 = cls._instance.get_match(nameMatch1)
			match1.register_player("yann")
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
			return False, "match does not exist", None
		elif username in self.registered_players_total:
			return False, "player already registered", None
		elif not (match.register_player(username)):
			return False, "game full", None
		self.registered_players_total.append(username)
		return True, "", match
	
	def remove_registered_player(self, player):
		self.registered_players_total.remove(player)
	
	def	join(self, username, match):
		if not match:
			return False, "match does not exist"
		elif username not in match.get_registered_players():
			return False, "player not registered for this match"
		elif len(match.get_registered_players()) != 2:
			return False, "not enough players registered"
		match.add_player_to_gamedata(username)
		return True, ""
	
	def	leave(self, username, match):
		if not match:
			return False, "match does not exist"
		elif username not in match.get_registered_players():
			return False, "player not registered for this match"
		print("before remove player:", match.get_registered_players())
		self.remove_registered_player(username)
		match.leave_match(username)
		print("after remove player:", match.get_registered_players())
		if len(match.get_registered_players()) == 0:
			print("DELETING MATCH")
			self.delete_match(match)
		return True, ""
	
	#player in first position in registered players hosts the game
	def	should_host_game(self, username, match):
		if username == match.get_registered_players()[1]:
			return True
		return False
	
	def add_match(self, match_id) -> bool:
		if match_id in self.matches:
			return False, "match name already exists"
		self.matches[match_id] = Match(match_id)
		return True, ""
	
	def	create_local_match(self, match_id) -> bool:
		return Match(match_id)

	def get_match(self, match_id):
		return self.matches.get(match_id)
	
	def delete_match(self, match):
		del self.matches[match.group_name]

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
		self.modus = ""
		self.n_registered_players = 0
		self.registered_players = []

		self.game_data = {}

		self.data_template = {
			"score": 0,
			"moveUp": False,
			"moveDown": False,
			"direction": 0,
		}

	def	register_player(self, user_id) -> bool:
		if self.n_registered_players == 2:
			return False
		self.n_registered_players += 1
		self.registered_players.append(user_id)
		return True

	def	get_registered_players(self):
		return self.registered_players

	def	join_match(self, user_id) -> bool:
		if user_id in self.registered_players:
			pass

	def	add_player_to_gamedata(self, player_id):
		self.game_data[player_id] = copy.deepcopy(self.data_template)
	
	def	leave_match(self, username):
		self.n_registered_players -= 1
		self.registered_players.remove(username)
			


