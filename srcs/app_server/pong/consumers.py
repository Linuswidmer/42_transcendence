from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asyncio import Lock
import json
import asyncio
from asgiref.sync import sync_to_async
import pygame
import time
import threading

# class PlayerConsumer(AsyncWebsocketConsumer):
# 	async def connect(self):
# 		self.group_name = "snek_game"
# 		# Join a common group with all other players
# 		await self.channel_layer.group_add(self.group_name, self.channel_name)
# 		await self.accept()

# 	# Send game data to group after a Tick is processed
# 	async def game_update(self, event):
# 		# Send message to WebSocket
# 		state = event["state"]
# 		await self.send(json.dumps(state))

# 	# Receive message from Websocket
# 	async def receive(self, text_data=None, bytes_data=None):
# 		content = json.loads(text_data)
# 		msg_type = content["type"]
# 		msg = content["msg"]
# 		if msg_type == "direction":
# 			return await self.direction(msg)
# 		elif msg_type == "join":
# 			return await self.join(msg)

clock = pygame.time.Clock()

class GameEngine(threading.Thread):
	def run(self) -> None:
		i = 0
		while True:
			dt = clock.tick(6)
			# self.broadcast_state(self.state)
			print("counter", i)
			i += 1


engine = GameEngine()

# Start the thread (which will execute the run method)
engine.start()