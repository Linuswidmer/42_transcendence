import json
import uuid
import asyncio
import time
import logging
import django

django.setup()

from adjectiveanimalnumber import generate
from .pong_ai_opponent import AIPongOpponent
from .GameDataCollector import GameDataCollector
from django.contrib.auth.models import User
import asyncio
from asgiref.sync import sync_to_async

logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.INFO)

from channels.generic.websocket import AsyncWebsocketConsumer

from pong_online.pong_ai_opponent import AIPongOpponent
from pong_online.pong_game import Pong
from pong_online.lobby import Lobby

from enum import Enum


class apiConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = str(uuid.uuid4())
		self.lobby = Lobby()
		self.listen_group_name = None
		self.listen_match = None

	async def connect(self):
		await self.accept()

		await self.send(
			text_data=json.dumps({"type": "connect", "api_id": self.id})
		)

	async def disconnect(self, close_code):
		await self.send(
			text_data=json.dumps({"type": "disconnect", "api_id": self.id, "reason": close_code})
		)
		await self.close()

	async def receive(self, text_data):
		print("api_text_data: ", text_data)
		# Split the received text into command and arguments
		tokens = text_data.strip().split()
		command = tokens.pop(0)
		option = tokens.pop(0) if tokens else None
		args = tokens

		response = command + ": "
		if command == "match":
			if not option:
				response += "no option provided"

			elif option == "list":
				response += json.dumps(self.lobby.get_all_matches())

			elif option == "create" and len(args) == 1:
				if self.lobby.add_match(args[0]):
					response += "created match successfully"
				else:
					response += option + ": match name already exists"

			elif option == "addplayer" and len(args) == 2:
				success, message, match = self.lobby.register_player_match(args[1], args[0])
				if success:
					response += "added player successfully"
				else:
					response += option + ": " + message

			elif option == "listen" and len(args) == 1:
				if await self.listen_to_match(args[0]):
					return
				else:
					response += option + ": valid arguments are a valid match ID or stop"
			else:
				response += option + ": not a valid option"

		elif command == "exit":
			await self.disconnect("user closed connection")
			return
		
		elif command == "listen":
			if await self.listen_to_match(option):
				return
			else:
				response += option + ": not a valid option"

		else:
			response += "invalid command"

		await self.send(response)
	
	async def listen_to_match(self, option):
		if option == "stop":
			print("Listen stop")
			if self.listen_group_name:
				await self.channel_layer.group_discard(self.listen_group_name, self.channel_name)
				self.listen_group_name = None
			return True
		elif option in self.lobby.get_all_matches():
			print("Listen start")
			self.listen_group_name = option
			self.listen_match = self.lobby.get_match(option)
			await self.channel_layer.group_add(self.listen_group_name, self.channel_name)
			return True
		return False

	async def	show_stats_end_game(self, event):
		await self.channel_layer.group_discard(self.listen_group_name, self.channel_name)
		self.listen_group_name = None
		self.listen_match = None

	async def group_game_state_update(self, event):
		# print("game_state:", " leon:", event["entity_data"]["leon"]["relativeY"], " local_opponent:", event["entity_data"]["local_opponent"]["relativeY"])
		extracted_data = {name: event["entity_data"][name] for name in self.listen_match.get_registered_players()}
		if event["entity_data"]["game_over"]:
			response = "Game over: " + str(extracted_data)
		else:
			response = extracted_data

		# await asyncio.sleep(3)
		await self.send(
			text_data=json.dumps(response)
		)


class MultiplayerConsumer(AsyncWebsocketConsumer):
	#global class variable to try some things without the db
	n_connected_websockets = 0

	update_lock = asyncio.Lock()

	async def load_generated_names_db_async(self):
		await sync_to_async(self.lobby.load_generated_names_db)()
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		MultiplayerConsumer.n_connected_websockets += 1
		print("number of connected websockets:", MultiplayerConsumer.n_connected_websockets)
		
		self.username = ""
		self.game_group_name = ""
		self.tournament_group_name = ""
		self.match = None
		self.hosts_game = False
		# set True when match is joined
		self.in_game = False
		# set True when match has started
		self.is_playing = False
		# set True when tournament has started
		self.tournament_started = False
		#Load all the game and tournaments from the db, to proof the 
		# generated later on, to avoid duplicates
		self.lobby = Lobby()
		asyncio.create_task(self.load_generated_names_db_async())

	#is called when connection from client to websocket (set up in routing.py) is
	#established. is for now established when user enters the lobby site
	async def connect(self):
		#accept ws connection
		await self.accept()

		await self.channel_layer.group_add(
			"lobby", self.channel_name
		)

	async def disconnect(self, close_code):
		pass
		# await self.channel_layer.group_discard(
		# 	"lobby", self.channel_name
		# )
		# await self.channel_layer.group_discard(
		# 	self.game_group_name, self.channel_name
		# )

	#everything that the client send through the websocket is received here
	#everything that is send by the client needs to have a type field
	#describing the type of message to deal with the information accordingly
	async def receive(self, text_data):
		logger.debug("data received in receive: %s", text_data)
		print("receive:", text_data)

		json_from_client = json.loads(text_data)

		message_type = json_from_client.get("type", "")

		if message_type == "username":
			self.username = json_from_client.get("username", "")
		
		# to indicate that the player is playing (not like in_game)
		if message_type == "start":
			await self.channel_layer.group_send(
					self.game_group_name,
					{"type": "set_is_playing"}
				)			
		print("...................")
		print("consumer: ", self.username, " | in_game: ", self.in_game, " | is_playing: ", self.is_playing, " | in_tm: ", self.tournament_started)
		print("game_group: ", self.game_group_name, " | tournament_group: ", self.tournament_group_name)
		print("matches: ", self.lobby.matches)
		print("tournaments: ", self.lobby.tournaments)
		print("registered players", self.lobby.registered_players_total)
		print("...................")

		# if a client cloeses the window or leaves the page, this is
		if message_type == "player_left":
			#player left during a match --> loses 
			if (self.in_game and self.is_playing):
				print("#1")
				await self.channel_layer.group_send(
					self.game_group_name,
					{"type": "end_game_player_left", "player": json_from_client.get("player", "")},
				)
			#player left before a match started, that is not a tournament --> leaves game
			elif (self.in_game and not self.is_playing and not self.tournament_group_name):
				print("#2")
				await self.process_lobby_update_in_consumer({"action": "leave"})
				await self.channel_layer.group_send(
					"lobby",
					{"type": "group_lobby_update"}
				)
			#player left tournament lobby before tournament started --> leaves tournament
			elif (not self.in_game and self.tournament_group_name and not self.tournament_started):
				print("#3")
				await self.process_lobby_update_in_consumer({"action": "leave_tournament", "tournament_id": self.tournament_group_name})
			#player left before a match started in a tournament --> loses
			elif (self.in_game and self.tournament_started):
				print("#4")
				#simulate the game as played
				asyncio.create_task(self.game_loop(self.match.modus))
				await self.channel_layer.group_send(
					self.game_group_name,
					{"type": "end_game_player_left", "player": self.username},
				)
			#player left the tournament lobby after the tournament started --> loses next game
			elif (not self.in_game and self.tournament_started):
				print("#5")
				tournament = self.lobby.tournaments[self.tournament_group_name]
				# add § in front of the player name
				for i in range(len(tournament.players)):
					if tournament.players[i] == self.username:
						tournament.players[i] = "§" + tournament.players[i]
				#await self.process_lobby_update_in_consumer({"action": "leave_tournament", "tournament_id": self.tournament_group_name})


		#if a client clicks on a link/button in the navbar 		
		if message_type == "reset_consumer_after_unusual_game_leave" or message_type == "leave":
			if (self.in_game and self.is_playing):
				print("#6")
				await self.channel_layer.group_send(
					self.game_group_name,
					{"type": "end_game_player_left", "player": self.username},
				)
			elif (self.in_game and not self.is_playing and not self.tournament_group_name):
				print("#7")
				await self.process_lobby_update_in_consumer({"action": "leave"})
				await self.channel_layer.group_send(
					"lobby",
					{"type": "group_lobby_update"}
				)
			elif (self.tournament_group_name and not self.in_game and not self.tournament_started):
				print("#8")
				await self.process_lobby_update_in_consumer({"action": "leave_tournament", "tournament_id": self.tournament_group_name})
			elif (self.in_game and self.tournament_started):
				print("#9")
				#simulate the game as played
				asyncio.create_task(self.game_loop(self.match.modus))
				await self.channel_layer.group_send(
					self.game_group_name,
					{"type": "end_game_player_left", "player": self.username},
				)
				#await self.process_lobby_update_in_consumer({"action": "leave_tournament", "tournament_id": self.tournament_group_name})
			elif (not self.in_game and self.tournament_started):
				print("#10")
				tournament = self.lobby.tournaments[self.tournament_group_name]
				# add § in front of the player name
				for i in range(len(tournament.players)):
					if tournament.players[i] == self.username:
						tournament.players[i] = "§" + tournament.players[i]
				await self.process_lobby_update_in_consumer({"action": "leave_tournament", "tournament_id": self.tournament_group_name})

		# if the pong_online js was loaded from the client it needs some data
		# to fill the view
		if message_type == "get_game_data":
			await self.send_initial_game_view_data()

		if message_type == "start" and self.hosts_game:
			logger.debug("start game with modus:%s", self.match.modus)
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "send_to_group", "identifier": "start_game"},
			)
			asyncio.create_task(self.game_loop(self.match.modus))

		if (self.tournament_group_name and not self.in_game and message_type == "tournament_lobby_update"):
			json_from_client["type"] = "group_tournament_update"
			await self.channel_layer.group_send(
				json_from_client.get("tournament_id"),
				json_from_client,
			)
		
		#only process lobby updates when not in // only leave when not in a running tournament
		if (not self.in_game and message_type == "lobby_update") or (message_type == "leave" and not self.tournament_started):
			#process button presses and update lobby content if necessary
			updated_lobby_info = await self.process_lobby_update_in_consumer(json_from_client)
			logger.debug("updated_lobby_info:%s", updated_lobby_info)
			#publish lobby info to all users so they can update the content
			if updated_lobby_info is not None:
				await self.channel_layer.group_send(
					"lobby",
					updated_lobby_info,
				)

		#we call process keypress to update the keypress in our
		#game_data. if one client sends a keypress. the process_keypress
		#function is called in both consumers
		#it is send over our game_group because only players in the group
		#should receive it
		if message_type == "keypress":
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "process_keypress",
				"playerId": json_from_client.get("playerId", ""),
	 			"action": json_from_client.get("action", "")},
			)

	async def set_is_playing(self, event):
		self.is_playing = True
		#print("consumer: ", self.username, " | in_game: ", self.in_game, " | is_playing: ", self.is_playing)

	async def send_initial_game_view_data(self):
		#for remote get the match from the lobby. Fix that the key is sent in this request
		data = {}
		data["type"] = "send_to_group"
		data["identifier"] = "deliver_init_game_data"

		#Find 
		match = self.lobby.get_match_by_player_id(self.username)
		if not match:
			for tm in self.lobby.tournaments.values():
				match = tm.get_match_for_player_id(self.username)
			if not match:
				match = self.match

		data["modus"] = match.modus
		if len(match.registered_players) == 1:
			data["match_name"] = match.group_name
			data["player1"] = match.registered_players[0]
		elif len(match.registered_players) == 2:
			data["match_name"] = match.group_name
			data["player1"] = match.registered_players[0]
			data["player2"] = match.registered_players[1]
		# await asyncio.sleep(2)
		await self.channel_layer.group_send(
			self.game_group_name,
			data,
		)

	#register: put consumer in group (match_id as group_name) -> thats were game updates will be published to
	async def process_lobby_update_in_consumer(self, json_from_client):
		action = json_from_client.get("action", "")
		match_id = json_from_client.get("match_id", "")
		tournament_id = json_from_client.get("tournament_id", None)
		modus = json_from_client.get("modus", "")
		ai_level = json_from_client.get("ai_level", None)
		tm_size = json_from_client.get("tm_size", "4")
		
		#check if registered -> if not try to register then join
		if action == "join" and modus == "remote":

			# if user already registered -> error
			if self.lobby.check_user_registered(self.username) and not tournament_id:
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot join match: player is already registered"}))
				return None
			
			match = self.lobby.get_match_by_player_id(self.username)
			
			#register user and add to game group
			if not match:
				# if match has tournament id get the match from tournament and not the lobby
				if tournament_id != None:
					tournament = self.lobby.get_tournament(tournament_id)
					match = tournament.get_match(match_id)
				else:
					match = self.lobby.get_match(match_id)						
				success, message = self.lobby.register_player_match(
						self.username, match
						)
				if success:
					self.game_group_name = match_id
					self.match = match
					await self.channel_layer.group_add(
						self.game_group_name, self.channel_name
					)
				else:
					await self.send(text_data=json.dumps({"type": "error", "message": "Cannot join match: match is already full"}))
					return

			#if user is registered to this game -> join
			if match.group_name == match_id:
				success, message = self.lobby.join(self.username, match)
				if success:
					await self.join_remote_game()
				else:
					json_from_client["error"] = message

		if action == "create":
			if self.lobby.check_user_registered(self.username):
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot create match: player is already registered"}))
				return None
			self.lobby.add_match(modus)

		if action == "leave":
			success, message = self.lobby.leave(self.username, self.match)
			if success:
				await self.send_initial_game_view_data()
				self.game_group_name = ""
				self.tournament_group_name = ""
				self.in_game = False
				self.is_playing = False
				self.match = None
				self.hosts_game = False
			else:
				json_from_client["error"] = message

		if action == "create_tournament":
			if self.lobby.check_user_registered(self.username):
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot create tournament: player is already registered"}))
				return None
			tournament_id = await self.lobby.add_tournament(self.username, int(tm_size))
			self.tournament_group_name = tournament_id
			await self.send(text_data=json.dumps({"type": "join_tournament", "tournament_id": tournament_id}))
			await self.channel_layer.group_add(
					tournament_id, self.channel_name
			)

		if action == "join_tournament":
			if self.lobby.check_user_registered(self.username):
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot join tournament: player is already registered"}))
				return None
			success, message = self.lobby.register_player_tournament(self.username, tournament_id)
			if success:
				self.tournament_group_name = tournament_id
				await self.send(text_data=json.dumps({"type": "join_tournament", "tournament_id": tournament_id}))
				await self.channel_layer.group_add(
					tournament_id, self.channel_name
				)
			else:
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot join tournament: tournament is already full"}))
				return
		
		if action == "leave_tournament":
			print("leave tournament called by: ", self.username)
			success, message = self.lobby.unregister_player_tournament(self.username, tournament_id)
			print("success: ", success, " | message: ", message)
			if success:
				self.game_group_name = ""
				self.tournament_group_name = ""
				self.in_game = False
				self.is_playing = False
				self.tournament_started = False
				self.match = None
				self.hosts_game = False
				await self.send(text_data=json.dumps({"type": "leave_tournament", "tournament_id": tournament_id}))
				await self.channel_layer.group_discard(
    				tournament_id, self.channel_name
				)
				json_from_client["type"] = "group_lobby_update"
				await self.channel_layer.group_send(
					"lobby",
					json_from_client,
				)
				json_from_client["type"] = "group_tournament_update"
				json_from_client["tournament_id"] = tournament_id
				await self.channel_layer.group_send(
					tournament_id,
					json_from_client,
				)
				return None
			else:
				json_from_client["error"] = message
		

		if action == "join" and (modus == "local" or modus == "ai"):
			if self.lobby.check_user_registered(self.username):
				await self.send(text_data=json.dumps({"type": "error", "message": "Cannot join match: player is already registered"}))
				return None
			
			if (ai_level):
				await self.join_local_game(modus, int(ai_level))
			else:
				await self.join_local_game(modus)
			return None
			
		json_from_client["type"] = "group_lobby_update"
		return json_from_client

	async def join_local_game(self, modus, ai_level=None):
		init_data = {}
		init_data["type"] = "join"
		init_data["modus"] = modus

		if modus == "ai":
			local_opponent_name = "AI_Ursula"
		if modus == 'local':
			local_opponent_name = 'DUMP_LOCAL'
		self.in_game = True
		self.hosts_game = True
		self.match = self.lobby.create_local_match(modus, ai_level)
		self.match.add_player_to_gamedata(local_opponent_name)
		self.match.add_player_to_gamedata(self.username)
		self.match.registered_players.append(local_opponent_name)
		self.match.registered_players.append(self.username)
		self.game_group_name = self.match.group_name
		init_data["match_name"] = self.match.group_name
		
		await self.channel_layer.group_add(
			self.game_group_name, self.channel_name
		)
		await self.send(text_data=json.dumps(init_data))

	async def join_remote_game(self):
		self.in_game = True
		if self.lobby.should_host_game(self.username, self.match):
			self.hosts_game = True
		await self.send(text_data=json.dumps({"type": "join", "modus": "remote"}))


	async def group_lobby_update(self, event):
		basic_update = {"type": "lobby_update"}
		
		#is this important???
		if "error" in event: #and self.username in event["username"]:
			basic_update["error"] = event["error"]

		#return all matches with registered players to display the lobby in the fronend
		matches_info = self.lobby.get_all_matches()
		tournaments_info = self.lobby.get_all_tournaments()
		basic_update["matches_info"] = matches_info
		basic_update["tournaments_info"] = tournaments_info
		await self.send(
			text_data=json.dumps(basic_update)
		)

	async def end_game_player_left(self,event):
		print("end_game_player_left called by: ", self.username)
		self.in_game = False
		self.is_playing = False
		if self.hosts_game:
			losing_player = event["player"]
			if self.match.registered_players[0] == losing_player:
				winning_player = self.match.registered_players[1]
			else:
				winning_player = self.match.registered_players[0]
			self.match.game_data[winning_player]["score"] = 3

	async def register_opponent(self, opponent, match_id):
		print("register opponent called by ", self.username)	
		tournament = self.lobby.get_tournament(self.tournament_group_name)
		match = tournament.get_match(match_id)

		print("match players: ", match.registered_players)
					
		success, message = self.lobby.register_player_match(opponent, match)
		print("success register_player_match: ", success, " message: ", message)
		success, message = self.lobby.join(opponent, match)
		print("success lobby.join: ", success, " message: ", message)


	async def group_tournament_update(self, event):
		basic_update = {"type": "tournament_lobby_update"}

		if "error" in event and self.username in event["username"]:
			basic_update["error"] = event["error"]

		if "action" in event and "redirect_to_tournament_stats" in event["action"]:
			self.game_group_name = ""
			self.tournament_group_name = ""
			self.in_game = False
			self.is_playing = False
			self.tournament_started = False
			self.match = None
			self.hosts_game = False
			await self.send(
				text_data=json.dumps({"type": "redirect_to_tournament_stats", "tournament_id": event["tournament_id"]})
			)
			return None

		tournament_id = event["tournament_id"]
		tournament = self.lobby.tournaments[tournament_id]

		# print("---------------")
		# print("in TM update from ", self.username)
		# print("tournament players: ", tournament.players)
		# print("tournament number of players: ", tournament.number_players, " | round: ", tournament.round)
		# print("---------------")

		# if full do matchmaking and send start_round to all group members
		if (len(tournament.matches) > 0 and len(tournament.players) == tournament.number_players - tournament.round * tournament.number_players // 2):
			tournament.visible_in_lobby = False
			self.tournament_started = True
			if self.username in tournament.players:
				match_index = tournament.players.index(self.username) // 2
				match_id = tournament.matches[match_index].group_name
				opponent = tournament.get_opponent(self.username)
				print('opponent of ', self.username, ' is ', opponent)
				#check if opponent is still in TM:
				if not opponent.startswith('§'):
					basic_update["match_id"] = match_id
					basic_update["action"] = "start_tournament_round"
				elif opponent.startswith('§'):
					print(self.username, ' start both games and leave')
					await self.register_opponent(opponent[1:], match_id)
					await self.process_lobby_update_in_consumer({type: 'lobby_update', 'action': 'join', 'match_id': match_id, 'tournament_id': tournament_id, 'username': self.username, 'modus': 'remote'})
					self.hosts_game = True
					# remove § in front of the player name
					for i in range(len(tournament.players)):
						if tournament.players[i] == opponent:
							tournament.players[i] = opponent[1:]
					asyncio.create_task(self.game_loop("remote"))
					await self.end_game_player_left({"player": opponent[1:]})
					return

		basic_update["tournament_id"] = tournament_id
		basic_update["players"] = tournament.players
		basic_update["tournament_data"] = tournament.data

		await self.send(
			text_data=json.dumps(basic_update)
		)

	async def send_to_group(self, event):
		#check again
		#if ("identifier" in event and event["identifier"] == "game_end"):
			#self.game_group_name = ""
		if ("game_over" in event and event["game_over"] == True):
			self.in_game = False
			self.is_playing = False
			return
		await self.send(
			text_data=json.dumps(event)
		)
	
	async def	show_stats_end_game(self, event):
		await self.send(
			text_data=json.dumps({
				"type": "redirect_to_game_page",
				"matchName": self.match.group_name,
				"user": self.username
				})
		)
	
	async def	show_tournament_lobby(self, event):
		if not "finished" in event:
			await self.send(text_data=json.dumps({"type": "redirect_to_tournament_lobby", "tournament_id": event["tournament_id"]}))
			await self.channel_layer.group_send(
				event["tournament_id"],
				{"type": "group_tournament_update", "tournament_id" : event["tournament_id"]},
			)	

	#update game_data with keypress, if we are in a consumer that
	#is not hosting the game, we ignore it
	async def process_keypress(self, keypress):
		if not self.hosts_game:
			return

		# triggered if this function is called with wrong argument for keypress
		if "action" not in keypress or "playerId" not in keypress:
			logger.warning("action are playerid need to be contained for process keypress to work")
			return
		
		action = keypress["action"]
		player_id = keypress["playerId"]
		if action == "moveUp":
			self.match.game_data[player_id]["moveUp"] = True
		elif action == "moveDown":
			self.match.game_data[player_id]["moveDown"] = True
		elif action == "stopMoveUp":
			self.match.game_data[player_id]["moveUp"] = False
		elif action == "stopMoveDown":
			self.match.game_data[player_id]["moveDown"] = False

		if self.match.game_data[player_id]["moveUp"] and not self.match.game_data[player_id]["moveDown"]:
			self.match.game_data[player_id]["direction"] = -1
		elif self.match.game_data[player_id]["moveDown"] and not self.match.game_data[player_id]["moveUp"]:
			self.match.game_data[player_id]["direction"] = 1
		else:
			self.match.game_data[player_id]["direction"] = 0


	def create_data_collector(self, modus, username1, username2, matchName, tournament):
		try:
			user1 = User.objects.get(username=username1)
			user2 = User.objects.get(username=username2)
		except User.DoesNotExist:
			# Handle the case where one or both users don't exist
			raise ValueError("One or both users do not exist.")

		return GameDataCollector(left_player=user1, right_player=user2, matchName=matchName, type=modus, tournament=tournament)

	
	#i dont think we need a lock here, as we work with the instances own game_data
	#every instance has its own game_data
	#when an update happens, all game_datas are updated
	#here we could import the game from another file to keep things separated
	async def game_loop(self, modus):
		players = self.match.registered_players
		print("AI LEVEL: ", self.match.ai_level)
		self.gdc = await sync_to_async(self.create_data_collector)(modus, players[1], players[0], self.match.group_name, self.match.tournament_id)
		logger.debug("new game loop started")
		pong_instance = Pong(self.gdc)
		FPS = 60
		AI_REFRESH_THRESHOLD = 1
		iteration_time = 1 / FPS
		if modus == "ai":
			ai = AIPongOpponent(pong_instance, iteration_time, self.match.ai_level)
			ai_refresh_timer = time.time()
		should_run = True
		initial_entity_data = pong_instance.get_initial_entity_data(self.match.game_data)
		await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "send_to_group", "identifier": "initial_game_data", 
	 			"initial_entity_data": initial_entity_data,
				"iteration_time": iteration_time, "modus": modus},
		)
		while should_run:
			if modus == "ai":
				if (time.time() - ai_refresh_timer >= AI_REFRESH_THRESHOLD):
					ai.setGameState(pong_instance)
					ai_refresh_timer = time.time()
				ai_decision = ai.getAIDecision()
				self.match.game_data["AI_Ursula"]["direction"] = ai_decision
			#update entities with the iteration_time and keypresses
			entity_data = await pong_instance.update_entities(iteration_time, self.match.game_data, self.match.registered_players)
			should_run = not entity_data["game_over"]
			#send all entity data to clients, so they can render the game
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "send_to_group", "identifier": "game_update", "entity_data": entity_data},
			)
			await asyncio.sleep(iteration_time)

		#Prevent the 'beforeunload' to trigger the end game logic in the end_game_player_left()
		#and the game is over so it actually makes sense :D
		self.hosts_game = False

		await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "send_to_group", "game_over": True},
			)

		#remove player from registred after match, so the player can play again
		#also remove the match from the lobby and update the lobby
		if (modus == 'remote'):
			print('DELETE MATCH?: ', self.match.tournament_id)
			if (self.match.tournament_id == None):
				self.lobby.delete_match(self.match)
			self.lobby.remove_registered_player(players[0])
			self.lobby.remove_registered_player(players[1])
			if (self.match.tournament_id == None):
				await self.channel_layer.group_send(
						"lobby",
						{"type" : "group_lobby_update"},
				)

		if (self.match.tournament_id == None):
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "send_to_group", "identifier": "game_end",
	 			"matchName": self.match.group_name, "user": self.username},
			)
		else:
			tournament = self.lobby.get_tournament(self.match.tournament_id)
			#delete loser from tournamnt players
			#userstats1 belongs to he left (so the hosting player), which is the player[1]
			if self.gdc.django_userstats_1.score == 3:
				tournament.data[tournament.round][self.match.group_name]["winner"] = players[1]
				tournament.data[tournament.round][self.match.group_name]["loser"] = players[0]
				tournament.players.remove(players[0])
			else:
				tournament.data[tournament.round][self.match.group_name]["winner"] = players[0]
				tournament.data[tournament.round][self.match.group_name]["loser"] = players[1]
				tournament.players.remove(players[1])
			
			#delete this match from tournmanet matches
			tournament.matches.remove(self.match)

			message = {"type": "show_tournament_lobby", "tournament_id" : self.match.tournament_id}
			
			#if tournament is finished, delete from lobby and redirect to tournament stats
			if (len(tournament.matches) == 0):
				message["finished"] = "True"
				tournament.django_tournament.data = tournament.data
				await sync_to_async(tournament.django_tournament.save)()
				await self.channel_layer.group_send(
					self.match.tournament_id,
					{"type": "group_tournament_update", "action": "redirect_to_tournament_stats", "tournament_id": self.match.tournament_id},
				)
				self.lobby.delete_tournament(tournament)
				del tournament
				#here the group could be deleted
				return
			#increment tournament round if its last game of round
			else:
				if (len(tournament.players) == tournament.number_players - (tournament.round + 1) * tournament.number_players // 2):
					tournament.round += 1

			await self.channel_layer.group_send(
				self.game_group_name,
				message,
			)
