import json
import uuid
import asyncio
import math
import pygame

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

from pong.pong_game import Pong

class MultiplayerConsumer(AsyncWebsocketConsumer):
	#global class variable to try some things without the db
	n_connected_players = 0
	last_game_group_name = ""

	#remove later
	players = {}

	#remove later
	update_lock = asyncio.Lock()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		#for now assign a uuid. maybe later session id or smth
		self.player_id = str(uuid.uuid4())

		self.game_data = {}

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
		player_id = text_data_json["playerId"]
		

		if message_type == "thrust":
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "process_keypress", message_type: player_id},
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


	async def process_keypress(self, event):
		if "thrust" in event:
			player_id = event["thrust"]
			
			#toggle keypress if entry already exists between True and False
			#if it doesnt exist, create it and set it to True
			if player_id in self.game_data and "thrusting" in self.game_data[player_id]:
				self.game_data[player_id]["thrusting"] = not self.game_data[player_id]["thrusting"]
			else:
				self.game_data.setdefault(player_id, {})["thrusting"] = True



	#i dont think we need a lock here, as we work with the instances own game_data
	#every instance has its own game_data
	#when an update happens, all game_datas are updated
	#here we could import the game from another file to keep things separated
	async def game_loop(self):
		print("new game loop started")
		clock = pygame.time.Clock()
		pong_instance = Pong()
		FPS = 30
		while 1:
			#this determines the tickrate that our server can send updated
			#also dt enables us to see if our server can keep up with the tick rate
			#or if smth is slowing it down
			# dt = clock.tick(FPS) / 1000  # Amount of seconds between each loop
			# margin = 0.1
			# if dt > (1/FPS * (1 + margin)):
			# 	print("Warning: Server cannot keep up with the desired framerate.")
			positions = pong_instance.update_entities(0.01)

			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "state_update", "object_positions": positions},
			)
			await asyncio.sleep(0.005)
