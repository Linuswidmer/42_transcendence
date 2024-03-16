import json
import uuid
import asyncio
import math
import pygame

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class MultiplayerConsumer(AsyncWebsocketConsumer):
	MAX_SPEED = 5
	THRUST = 0.2


	players = {}

	update_lock = asyncio.Lock()

	async def connect(self):
		self.player_id = str(uuid.uuid4())
		await self.accept()

		game_group_name = str(uuid.uuid4()) 	
		print("game_group_name:", game_group_name)
		await self.channel_layer.group_add(
			game_group_name, self.channel_name
		)

		await self.send(
			text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
		)

		async with self.update_lock:
			self.players[self.player_id] = {
				"id": self.player_id,
				"x": 500,
				"y": 500,
				"facing": 0,
				"dx": 0,
				"dy": 0,
				"thrusting": False,
			}

		# if len(self.players) == 1:
		asyncio.create_task(self.game_loop(game_group_name))

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

		message_type = text_data_json.get("type", "")

		player_id = text_data_json["playerId"]

		player = self.players.get(player_id, None)

		if message_type == "thrust":
			player["thrusting"] = not player["thrusting"]

		if not player:
			return

	async def state_update(self, event):
		await self.send(
			text_data=json.dumps(
				{
					"type": "stateUpdate",
					"objects": event["objects"],
					"groupName": event["groupName"],
				}
			)
		)

	async def game_loop(self, group_name):
		print("new game loop started")
		while len(self.players) > 0:
			async with self.update_lock:
				for player in self.players.values():
					if player["thrusting"]:
						dx = self.THRUST * math.cos(player["facing"])
						dy = self.THRUST * math.sin(player["facing"])
						player["dx"] += dx
						player["dy"] += dy

						speed = math.sqrt(player["dx"] ** 2 + player["dy"] ** 2)
						if speed > self.MAX_SPEED:
							ratio = self.MAX_SPEED / speed
							player["dx"] *= ratio
							player["dy"] *= ratio

					player["x"] += player["dx"]
					player["y"] += player["dy"]
					
					# print(player)
			# print("publishing update to:", group_name)
			await self.channel_layer.group_send(
				group_name,
				{"type": "state_update", "objects": list(self.players.values()), "groupName": group_name},
			)
			await asyncio.sleep(3)
