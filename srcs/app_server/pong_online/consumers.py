import json
import uuid
import asyncio
import math
import time
import pygame
import logging
from adjectiveanimalnumber import generate

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

from pong_online.pong_game import Pong
from pong_online.lobby import Lobby

class apiConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = str(uuid.uuid4())

	async def connect(self):
		await self.accept()

		await self.send(
			text_data=json.dumps({"type": "connect", "api_id": self.id})
		)

	async def disconnect(self, close_code):
		await self.send(
			text_data=json.dumps({"type": "disconnect", "api_id": self.id})
		)

	async def receive(self, text_data):
		print(text_data)
		await self.send(
			text_data=json.dumps({"type": "receive", "api_id": self.id, "data": text_data})
		)




class MultiplayerConsumer(AsyncWebsocketConsumer):
	#global class variable to try some things without the db
	n_connected_players = 0
	# last_game_group_name = ""

	update_lock = asyncio.Lock()
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		MultiplayerConsumer.n_connected_players += 1
		print("n connected:", MultiplayerConsumer.n_connected_players)
		#for now assign a uuid. maybe later session id or smth
		# self.player_id = str(uuid.uuid4())
		self.username = ""
		self.game_group_name = ""

		self.lobby = Lobby()
		# self.match = self.lobby.get_match_by_player_id()

		self.in_game = False

		self.game_data = {
			# self.username: {
			# 	"score": 0,
			# 	"moveUp": False,
			# 	"moveDown": False,
			# 	"direction": 0,
			# },
			# "player2": {
			# 	"score": 0,
			# 	"moveUp": False,
			# 	"moveDown": False,
			# 	"direction": 0,
			# }
		}
		#set to true later for consumer that runs the game loop
		self.hosts_game = False

	#is called when connection from client to websocket (set up in routing.py) is
	#established
	async def connect(self):
		#accept ws connection
		await self.accept()

		await self.channel_layer.group_add(
			"lobby", self.channel_name
		)
		#send playerId to browser
		#probably remove this as i see now reason why the browser would want
		#or need to know the id that the server assigns
		# await self.send(
		# 	text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
		# )


		#assign user to its own group
		#probably here we consult the db to see if other players are available
		#in order to decide wether we join an already existing game or start
		#a new one -> should defenitely go to its own function. maybe even own file,
		#for matchmaking
		# async with self.update_lock:
		# 	MultiplayerConsumer.n_connected_players += 1
		
		# #equal amount of player -> join existing game
		# if MultiplayerConsumer.n_connected_players % 2 == 0:
		# 	self.game_group_name = MultiplayerConsumer.last_game_group_name
		# else:
		# 	self.hosts_game = True
		# 	self.game_group_name = str(uuid.uuid4())
		# 	MultiplayerConsumer.last_game_group_name = self.game_group_name

		#add player to group to send/receive updates
		# await self.channel_layer.group_add(
		# 	self.game_group_name, self.channel_name
		# )

		#add player to lobby



		#start game_loop if player is hosting
		# if self.hosts_game:
		# 	asyncio.create_task(self.game_loop())

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.game_group_name, self.channel_name
		)

	async def receive(self, text_data):
		print(text_data)
		text_data_json = json.loads(text_data)
		message_type = text_data_json.get("type", "")

		#we dont need to actually obtain the id from the client
		#we now it is our client because we are inside receive
		#so we can just send self.player_id to process keypress

		if message_type == "username":
			self.username = text_data_json.get("username", "")
			print(self.username)

		if message_type == "start" and self.hosts_game:
			print("start game")
			asyncio.create_task(self.game_loop())

		if not self.in_game and message_type == "lobby_update":
			if text_data_json["action"] == "register":
				success, message = self.lobby.register_player_match(
					self.username, text_data_json["match_id"]
				)
				if not success:
					text_data_json["error"] = message
				if success:
					self.game_group_name = text_data_json["match_id"]
					
					await self.channel_layer.group_add(
						self.game_group_name, self.channel_name
					)

			if text_data_json["action"] == "create":
				print("Create")
				success, message = self.lobby.add_match(str(generate()))
				if not success:
					text_data_json["error"] = message

			if text_data_json["action"] == "join":
				success, message = self.lobby.join(self.username, text_data_json["match_id"])
				if success:
					await self.join_game(text_data_json["match_id"])
					return
				else:
					text_data_json["error"] = message
			await self.channel_layer.group_send(
				"lobby",
				text_data_json,
			)

		#we call process keypress to update the keypress in our
		#game_data. if one client sends a keypress. the process_keypress
		#function is called in both consumers
		if message_type == "keypress":
			print("game group name keypress", self.username, self.game_group_name, type(self.game_group_name))
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "process_keypress",
				"playerId": self.username,
	 			"action": text_data_json.get("action", "")},
			)

	async def join_game(self, match_id):
		# self.game_group_name = "alex"
		if self.lobby.should_host_game(self.username, match_id):
			self.hosts_game = True
		match = self.lobby.get_match(match_id)
		players = match.get_registered_players()
		for player in players:
			self.game_data[player] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
		print("game_data", self.game_data)
		
		await self.send(text_data=json.dumps({"type": "join"}))


	async def lobby_update(self, event):
		basic_update = {"type": "lobby_update"}
		
		if "error" in event and self.username in event["username"]:
			basic_update["error"] = event["error"]
		
		

		#return all matches with registered players to display the lobby in the fronend
		matches_info = self.lobby.get_all_matches()
		basic_update["matches_info"] = matches_info
		await self.send(
			text_data=json.dumps(basic_update)
		)


	async def state_update(self, event):
		await self.send(
			text_data=json.dumps(event)
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
		print("keypress:", keypress)
		#update dictionary with other playerId the first time we receive a keypress
		# if player_id not in self.game_data:
		# 	self.game_data[player_id] = self.game_data["player2"] 
		# 	del self.game_data["player2"]

		if action == "moveUp":
			self.game_data[player_id]["moveUp"] = True
		elif action == "moveDown":
			self.game_data[player_id]["moveDown"] = True
		elif action == "stopMoveUp":
			self.game_data[player_id]["moveUp"] = False
		elif action == "stopMoveDown":
			self.game_data[player_id]["moveDown"] = False

		if self.game_data[player_id]["moveUp"] and not self.game_data[player_id]["moveDown"]:
			self.game_data[player_id]["direction"] = -1
		elif self.game_data[player_id]["moveDown"] and not self.game_data[player_id]["moveUp"]:
			self.game_data[player_id]["direction"] = 1
		else:
			self.game_data[player_id]["direction"] = 0

	#i dont think we need a lock here, as we work with the instances own game_data
	#every instance has its own game_data
	#when an update happens, all game_datas are updated
	#here we could import the game from another file to keep things separated
	async def game_loop(self):
		logger.debug("new game loop started")
		pong_instance = Pong()
		FPS = 3
		iteration_time = 1 / FPS
		while 1:
			# start_time = time.time()

			#update entities with the iteration_time and keypresses
			entity_data = pong_instance.update_entities(iteration_time, self.game_data)

			#send all entity data to clients, so they can render the game
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "state_update", "entity_data": entity_data},
			)
			await asyncio.sleep(iteration_time)

			# end_time = time.time()  # End time of the iteration
			# iteration_time_measured = end_time - start_time
			# margin = 0.1
			# if iteration_time_measured  > (iteration_time * (1 + margin)):
			# 	print("Warning: Server cannot keep up with the desired framerate.", iteration_time_measured, ">", iteration_time)
