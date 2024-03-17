import json
import uuid
import asyncio
import math
import pygame

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

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
		await self.send(
			text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
		)

		# print("n connected players", MultiplayerConsumer.n_connected_players)
		if MultiplayerConsumer.n_connected_players % 2 == 1:
			asyncio.create_task(self.game_loop(self.game_group_name))

		#broadcast group name to everyone
		# await self.channel_layer.group_send(
		# 	self.game_group_name,
		# 	{"type": "register_opponent", "playerId": self.player_id},
		# )

	async def disconnect(self, close_code):
		async with self.update_lock:
			if self.player_id in self.players:
				del self.players[self.player_id]

		#TODO handle proper disconnecting from all groups
		# await self.channel_layer.group_discard(
		# 	self.game_group_name, self.channel_name
		# )

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		print(text_data_json)

		message_type = text_data_json.get("type", "")
		print("msg type", message_type)

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
			text_data=json.dumps(self.game_data)
		)
	
	# async def register_opponent(self, event):
	# 	if "playerId" in event:
	# 		opponent_id = event["playerId"]
	# 		self.game_data[opponent_id] = {}


	async def process_keypress(self, event):
		if "thrust" in event:
			player_id = event["thrust"]
			
			if player_id in self.game_data and "thrusting" in self.game_data[player_id]:
				self.game_data[player_id]["thrusting"] = not self.game_data[player_id]["thrusting"]
			else:
				self.game_data.setdefault(player_id, {})["thrusting"] = True




	async def game_loop(self, group_name):
		print("new game loop started")
		while 1:
			# async with self.update_lock:
			# 	for player in self.players.values():
			# 		if player["thrusting"]:
			# 			dx = self.THRUST * math.cos(player["facing"])
			# 			dy = self.THRUST * math.sin(player["facing"])
			# 			player["dx"] += dx
			# 			player["dy"] += dy

			# 			speed = math.sqrt(player["dx"] ** 2 + player["dy"] ** 2)
			# 			if speed > self.MAX_SPEED:
			# 				ratio = self.MAX_SPEED / speed
			# 				player["dx"] *= ratio
			# 				player["dy"] *= ratio

			# 		player["x"] += player["dx"]
			# 		player["y"] += player["dy"]
					
					# print(player)
			await self.channel_layer.group_send(
				group_name,
				{"type": "state_update", "objects": list(self.game_data.values()), "groupName": group_name},
			)
			await asyncio.sleep(3)
