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
from channels.layers import get_channel_layer
from channels.consumer import SyncConsumer
import logging

logging.basicConfig(level=logging.INFO)

# class PlayerConsumer(AsyncWebsocketConsumer):
# 	async def connect(self):
# 		self.group_name = "tick_test"
# 		# Join a common group with all other players
# 		await self.channel_layer.group_add(self.group_name, self.channel_name)
# 		await self.accept()

# 	# Send game data to group after a Tick is processed
# 	# async def game_update(self, event):
# 	# 	# Send message to WebSocket
# 	# 	state = event["state"]
# 	# 	await self.send(json.dumps(state))

# 	# Receive message from Websocket
# 	async def receive(self, text_data=None, bytes_data=None):
# 		content = json.loads(text_data)
# 		print(content)
class PongConsumer(AsyncWebsocketConsumer):
	ready   = False
	lock = Lock()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# self.game_state = GameState()

	async def connect(self):
		# self.room_group_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = "tick_test"
		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		await self.accept()

		await self.send(text_data=json.dumps({
			'PongConsumer': "This message was send after connecting",
		}))

		thisdict = {
			"brand": "Ford",
			"model": "Mustang",
			"year": 1964
			}
		await self.join(thisdict)

	
	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

	async def join(self, msg: dict):
		await self.channel_layer.send(
			"game_engine",
			{"type": "player.new", "channel": self.channel_name},
		)

	async def receive(self, text_data):
		text_data_json = json.loads(text_data)
		print("PongConsumer received: ", text_data_json)

	async def game_update(self, event):
		print(event)
		# Send message to WebSocket
		await self.send(json.dumps(event))


class GameConsumer(SyncConsumer):
	def __init__(self, *args, **kwargs):
		"""
		Created on demand when the first player joins.
		"""
		super().__init__(*args, **kwargs)
		self.group_name = "tick_test"
		self.engine = GameEngine(self.group_name)
		# Runs the engine in a new thread
		self.engine.start()

	def player_new(self, event):
		self.engine.join_queue(event["player"])

	# def player_direction(self, event):
	# 	direction = event.get("direction", "UP")
	# 	self.engine.set_player_direction(event["player"], direction)
	
	def broadcast_state(self, counter: int) -> None:
		counter_json = json.dumps({'counter': counter})
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			self.group_name, {"type": "game_update", "counter": counter_json}
		)

clock = pygame.time.Clock()

class GameEngine(threading.Thread):
	def __init__(self, group_name, **kwargs):
		super(GameEngine, self).__init__(daemon=True, name="GameEngine", **kwargs)
		self.group_name = group_name
		self.channel_layer = get_channel_layer()
		self.logger = logging.getLogger('game_engine')

	def run(self) -> None:
		self.logger.info('GameEngine loop started')
		i = 0
		while True:
			dt = clock.tick(6)
			self.broadcast_state(i)
			self.logger.info('GameEngine loop running, counter: %s', i)
			i += 1

	def broadcast_state(self, counter: int) -> None:
		counter_json = json.dumps({'counter': counter})
		async_to_sync(self.channel_layer.group_send)(
			self.group_name, {"type": "game_update", "counter": counter_json}
		)

