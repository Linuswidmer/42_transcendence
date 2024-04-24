from uuid import uuid4
from adjectiveanimalnumber import generate
import copy
from .models import Tournaments, Games
from asgiref.sync import sync_to_async
import math
import json

class Lobby:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Lobby, cls).__new__(cls, *args, **kwargs)
			cls._instance.matches = {}
			cls._instance.tournaments = {}
			cls._instance.registered_players_total = []
			cls._instance.used_generated_names = set()
		return cls._instance

	def load_generated_names_db(self):
		games = Games.objects.all()
		tournaments = Tournaments.objects.all()
		for game in games:
			self.used_generated_names.add(game.matchName)
		for tm in tournaments:
			self.used_generated_names.add(tm.tournament_id)

	#return correct match instance to consumer
	def get_match_by_player_id(self, player_id):
		for match in self.matches.values():
			if player_id in match.registered_players:
				return match
		return None
	
	def get_all_matches(self):
		return {match_id: match.get_registered_players() for match_id, match in self.matches.items()}
	

	def get_all_tournaments(self):
		tournament_players = {}
		for tournament_id, tournament in self.tournaments.items():
			players = tournament.get_registered_players()
			if tournament.visible_in_lobby == True:
				tournament_players[tournament_id] = players
		return tournament_players
	
	# rename to join match
	def register_player_match(self, username, match):
		#match = self.get_match(match_id)
		if not match:
			return False, "match does not exist"
		elif username in self.registered_players_total:
			return False, "player already registered"
		elif not (match.register_player(username)):
			return False, "game full"
		self.registered_players_total.append(username)
		return True, ""

	def remove_registered_player(self, player):
		self.registered_players_total.remove(player)
	
	# rename to join tournament
	def register_player_tournament(self, username, tournament_id):
		tournament = self.get_tournament(tournament_id)
		if not tournament:
			return False, "tournament does not exist"
		elif username in self.registered_players_total:
			return False, "player already registered"
		elif not (tournament.register_player(username)):
			return False, "tournament full"
		#self.registered_players_total.append(username)
		return True, ""
	
	# rename to leave tournament
	def unregister_player_tournament(self, username, tournament_id):
		tournament = self.get_tournament(tournament_id)
		if not tournament:
			return False, "tournament does not exist"
		elif not (username in tournament.players):
			return False, "player not in tournament"
		tournament.players.remove(username)
		#self.registered_players_total.remove(username)
		#print(self.tournaments)
		if (len(tournament.players) == 0):
			del self.tournaments[tournament_id]
		return True, ""

	# rename to start game
	def	join(self, username, match):
		if not match:
			return False, "match does not exist"
		elif username not in match.get_registered_players():
			return False, "player not registered for this match"
		#we shouldnt need this anymore, because register and join where merged to one button
		# elif len(match.get_registered_players()) != 2:
		# 	return False, "not enough players registered"
		match.add_player_to_gamedata(username)
		return True, ""
	
	def	leave(self, username, match):
		if not match:
			return False, "match does not exist"
		elif username not in match.get_registered_players():
			return False, "player not registered for this match"
		match.leave_match(username)
		del match.game_data[username]
		if (match.modus == "remote"):
			self.remove_registered_player(username)
			if len(match.get_registered_players()) == 0:
				self.delete_match(match)
		return True, ""
	
	#player in second position in registered players hosts the game
	#this is necessary, because players can leave the lobby again
	def	should_host_game(self, username, match):
		registered_players = match.get_registered_players()
		if len(registered_players) == 2 and username == registered_players[1]:
			return True
		return False
	
	def generate_name(self):
		name = str(generate())
		while (name in self.used_generated_names):
			print('Name already in use: ', name)
			name = str(generate())
		self.used_generated_names.add(name)
		return name

	# rename to create_match
	def add_match(self, modus) -> bool:
		print('CREATE: ', modus)
		match_name = self.generate_name()
		self.matches[match_name] = Match(match_name, modus)
		return match_name

	def create_django_tournament(self, tournament_id):
		return Tournaments.objects.create(tournament_id=tournament_id)

	async def add_tournament(self, username) -> bool:
		tournament_id = self.generate_name()
		print('Create Tournamnet, generated name: ', tournament_id)
		self.tournaments[tournament_id] = Tournament(tournament_id, 4, self)
		self.tournaments[tournament_id].django_tournament = await sync_to_async(self.create_django_tournament)(tournament_id)
		self.tournaments[tournament_id].players.append(username)
		# self.registered_players_total.append(username) # Are you sure you need this?

		return tournament_id

	def load_generated_names_db(self):
		games = Games.objects.all()
		tournaments = Tournaments.objects.all()
		for game in games:
			self.used_generated_names.add(game.matchName)
		for tm in tournaments:
			self.used_generated_names.add(tm.tournament_id)
	
	def	create_local_match(self, modus) -> bool:
		match_id = self.generate_name()
		return Match(match_id, modus)

	def get_match(self, match_id):
		return self.matches.get(match_id)
	
	def get_tournament(self, tournament_id):
		return self.tournaments.get(tournament_id)
		
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
	def __init__(self, match_id, modus, tournament_id=None) -> None:
		#generate unique identifier for group communication
		self.group_name = match_id
		self.modus = modus
		self.n_registered_players = 0
		self.registered_players = []
		self.tournament_id = tournament_id

		self.game_data = {}

		self.data_template = {
			"score": 0,
			"moveUp": False,
			"moveDown": False,
			"direction": 0,
		}

	def	change_score(self, username, score):
		if username in self.registered_players:
			self.game_data[username]["score"] = score

	def move_paddle(self, username, direction):
		if username in self.registered_players:
			if direction == 1:
				self.game_data[username]["direction"] = 1
			elif direction == -1:
				self.game_data[username]["direction"] = -1
			elif direction == 0:
				self.game_data[username]["direction"] = 0

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
	
	
	# def	leave_match(self, user_id):
	# 	if user_id in self.registered_players:
	# 		self.n_registered_players -= 1
	# 		self.registered_players.discard(user_id)

class Tournament:
	def __init__(self, name, number_players, lobby) -> None:
		self.tournament_name = name
		self.players = []
		self.matches = []
		self.data = {}
		self.round = 0
		self.django_tournament = None
		self.visible_in_lobby = True
		self.number_players = number_players
		self.lobby = lobby
		self.generate_matches(number_players)

	def get_registered_players(self):
		return self.players

	def	register_player(self, user_id) -> bool:
		if len(self.players) == self.number_players:
			return False
		self.players.append(user_id)
		return True

	def get_match_for_player_id(self, player):
		for match in self.matches:
			if player in match.registered_players:
				return match
		return None

	def generate_matches(self, num_participants):
		games_per_round = int(num_participants / 2) #start, gets divided by two every time
		games_added = 0
		current_round = 0
		for i in range(num_participants - 1):
			if games_added == games_per_round:
				games_added = 0
				games_per_round /= 2
				current_round += 1
			match_id = self.lobby.generate_name()
			if current_round in self.data:
				# If the round already exists, add the match to it
				self.data[current_round][match_id] = {
					"winner": "None",
					"loser": "None"
				}
			else:
				# If the round doesn't exist, create it and add the match
				self.data[current_round] = {
					match_id: {
						"winner": "None",
						"loser": "None"
					}
				}
			games_added += 1
			self.matches.append(Match(match_id, "remote", self.tournament_name))
		print(json.dumps(self.data, indent=4))

	def get_match(self, match_id):
		for match in self.matches:
			if match.group_name == match_id:
				return match
