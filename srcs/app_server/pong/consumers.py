import json
import uuid
import asyncio
import math
import time
import pygame
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

from pong.pong_game import Pong

class MultiplayerConsumer(AsyncWebsocketConsumer):
	#global class variable to try some things without the db
	n_connected_players = 0
	last_game_group_name = ""



	#remove later
	update_lock = asyncio.Lock()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#for now assign a uuid. maybe later session id or smth
		self.player_id = str(uuid.uuid4())

		self.game_data = {
			self.player_id: {
				"score": 0,
				"direction": 0,
			},
			"player2": {
				"score": 0,
				"direction": 0,

			}
		}

		# self.player_data = {
		# 	"id": self.player_id,
		# 	"thrusting": False,
		# }
		self.hosts_game = False

	#is called when connection from client to websocket (set up in routing.py) is
	#established
	async def connect(self):
		#accept ws connection
		await self.accept()

		#assign user to its own group
		#probably here we consult the db to see if other players are available
		#in order to decide wether we join an already existing game or start
		#a new one
		async with self.update_lock:
			MultiplayerConsumer.n_connected_players += 1
		
		#equal amount of player -> join existing game
		if MultiplayerConsumer.n_connected_players % 2 == 0:
			self.game_group_name = MultiplayerConsumer.last_game_group_name
		else:
			self.hosts_game = True
			self.game_group_name = str(uuid.uuid4())
			MultiplayerConsumer.last_game_group_name = self.game_group_name
	
		print("game_group_name:", self.game_group_name)

		#needs to always happen
		await self.channel_layer.group_add(
			self.game_group_name, self.channel_name
		)

		#send playerId to browser
		#probably remove this as i see now reason why the browser would want
		#or need to know the id that the server assigns
		await self.send(
			text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
		)

		# print("n connected players", MultiplayerConsumer.n_connected_players)
		if MultiplayerConsumer.n_connected_players % 2 == 1:
			asyncio.create_task(self.game_loop())

		#broadcast group name to everyone
		# await self.channel_layer.group_send(
		# 	self.game_group_name,
		# 	{"type": "register_opponent", "playerId": self.player_id},
		# )

	async def disconnect(self, close_code):
		# async with self.update_lock:
		# 	if self.player_id in self.players:
		# 		del self.players[self.player_id]

		#TODO handle proper disconnecting from all groups
		await self.channel_layer.group_discard(
			self.game_group_name, self.channel_name
		)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		print(text_data_json)

		message_type = text_data_json.get("type", "")
		print("msg type", message_type)

		#we dont need to actually obtain the id from the client
		#we now it is our client because we are inside receive
		#so we can just send self.player_id to process keypress
		# player_id = text_data_json["playerId"]
		

		if message_type == "keypress":
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "process_keypress",
				"playerId": text_data_json.get("playerId", ""),
	 			"action": text_data_json.get("action", "")},
			)


	async def state_update(self, event):
		await self.send(
			# text_data=json.dumps(
			# 	{
			# 		"type": "stateUpdate",
			# 		"objects": event["objects"],
			# 		"groupName": event["groupName"],
			# 	}
			# )
			text_data=json.dumps(event)
		)
	
	# async def register_opponent(self, event):
	# 	if "playerId" in event:
	# 		opponent_id = event["playerId"]
	# 		self.game_data[opponent_id] = {}


	async def process_keypress(self, keypress):
		if not self.hosts_game:
			return

		if "action" not in keypress or "playerId" not in keypress:
			logger.warning("action are playerid need to be contained for process keypress to work")
			return
		
		action = keypress["action"]
		player_id = keypress["playerId"]
		
		#update dictionary with other playerId the first time we receive a keypress
		if player_id not in self.game_data:
			self.game_data[player_id] = self.game_data["player2"] 
			del self.game_data["player2"]

		if action == "moveLeft":
			self.game_data[player_id]["direction"] = -1
		elif action == "moveRight":
			self.game_data[player_id]["direction"] = 1
		elif action == "stopMove":
			self.game_data[player_id]["direction"] = 0
			self.game_data[player_id]["direction"] = 0

			


	#i dont think we need a lock here, as we work with the instances own game_data
	#every instance has its own game_data
	#when an update happens, all game_datas are updated
	#here we could import the game from another file to keep things separated
	async def game_loop(self):
		print("new game loop started")
		clock = pygame.time.Clock()
		pong_instance = Pong()
		FPS = 0.5
		iteration_time = 1 / FPS
		while 1:
			start_time = time.time()
			#this determines the tickrate that our server can send updated
			#also dt enables us to see if our server can keep up with the tick rate
			#or if smth is slowing it down
			# dt = clock.tick(FPS) / 1000  # Amount of seconds between each loop
			positions = pong_instance.update_entities(iteration_time, self.game_data)

			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "state_update", "object_positions": positions, "game_data": self.game_data},
			)
			await asyncio.sleep(1 / FPS)

			end_time = time.time()  # End time of the iteration
			iteration_time_measured = end_time - start_time
			margin = 0.1
			if iteration_time_measured  > (iteration_time * (1 + margin)):
				print("Warning: Server cannot keep up with the desired framerate.")
