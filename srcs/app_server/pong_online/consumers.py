import json
import uuid
import asyncio
import time
import logging

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

class apiConsumer(AsyncWebsocketConsumer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = str(uuid.uuid4())
		self.lobby = Lobby()

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
		# Split the received text into command and arguments
		tokens = text_data.strip().split()
		command = tokens.pop(0)
		option = tokens.pop(0) if tokens else None
		args = tokens

		if command == "match":
			response = command + ": "
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
			else:
				response += option + ": not a valid option"

		elif command == "exit":
			await self.disconnect("user closed connection")
			return


		else:
			response += "invalid command"

		await self.send(response)




class MultiplayerConsumer(AsyncWebsocketConsumer):
	#global class variable to try some things without the db
	n_connected_websockets = 0

	update_lock = asyncio.Lock()
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		MultiplayerConsumer.n_connected_websockets += 1
		print("number of connected websockets:", MultiplayerConsumer.n_connected_websockets)
		#for now assign a uuid. maybe later session id or smth
		# self.player_id = str(uuid.uuid4())
		self.username = ""
		self.game_group_name = ""

		self.lobby = Lobby()
		# self.match = self.lobby.get_match_by_player_id()

		self.in_game = False

		self.game_data = {}

		self.match = None

		#set to true later for consumer that runs the game loop
		self.hosts_game = False

	#is called when connection from client to websocket (set up in routing.py) is
	#established. is for now established when user enters the lobby site
	async def connect(self):
		#accept ws connection
		await self.accept()

		await self.channel_layer.group_add(
			"lobby", self.channel_name
		)

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(
			"lobby", self.channel_name
		)
		await self.channel_layer.group_discard(
			self.game_group_name, self.channel_name
		)

	#everything that the client send through the websocket is received here
	#everything that is send by the client needs to have a type field
	#describing the type of message to deal with the information accordingly

	async def receive(self, text_data):
		logger.debug("data received in receive: %s", text_data)
		print("text data from client in receive:", text_data)

		json_from_client = json.loads(text_data)

		message_type = json_from_client.get("type", "")

		if message_type == "username":
			self.username = json_from_client.get("username", "")

		if message_type == "start" and self.hosts_game:
			logger.debug("start game with modus:%s", json_from_client["modus"])
			asyncio.create_task(self.game_loop(json_from_client["modus"]))

		#only process lobby updates. when not inga,e
		if not self.in_game and message_type == "lobby_update":
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

	#register: put consumer in group (match_id as group_name) -> thats were game updates will be published to
	async def process_lobby_update_in_consumer(self, json_from_client):
		action = json_from_client.get("action", "")
		match_id = json_from_client.get("match_id", "")
		modus = json_from_client.get("modus", "")

		if action == "register":
			success, message, match = self.lobby.register_player_match(
				self.username, match_id
			)
			if success:
				self.game_group_name = match_id
				self.match = match
				await self.channel_layer.group_add(
					self.game_group_name, self.channel_name
				)
			else:
				json_from_client["error"] = message

		if action == "create":
			success, message = self.lobby.add_match(str(generate()))
			if not success:
				json_from_client["error"] = message

		if action == "join" and modus == "remote":
			success, message = self.lobby.join(self.username, self.match)
			if success:
				await self.join_remote_game()
				return None
			else:
				json_from_client["error"] = message
		
		if action == "join" and (modus == "local" or modus == "ai"):
			await self.join_local_game(modus)
			return None
			
		
		json_from_client["type"] = "group_lobby_update"
		return json_from_client

	async def join_local_game(self, modus):
		local_opponent_name = modus + "_opponent"
		if modus == "ai":
			local_opponent_name = "AI_Ursula"
		self.in_game = True
		self.hosts_game = True
		match_id = generate()
		self.match = self.lobby.create_local_match(match_id)
		self.match.add_player_to_gamedata(self.username)
		self.match.add_player_to_gamedata(local_opponent_name)
		self.game_group_name = match_id
		
		await self.channel_layer.group_add(
			self.game_group_name, self.channel_name
		)
		await self.send(text_data=json.dumps({"type": "join", "modus": modus}))

	async def join_remote_game(self):
		self.in_game = True
		if self.lobby.should_host_game(self.username, self.match):
			self.hosts_game = True
		
		await self.send(text_data=json.dumps({"type": "join", "modus": "remote"}))


	async def group_lobby_update(self, event):
		basic_update = {"type": "lobby_update"}
		
		if "error" in event and self.username in event["username"]:
			basic_update["error"] = event["error"]

		#return all matches with registered players to display the lobby in the fronend
		matches_info = self.lobby.get_all_matches()
		basic_update["matches_info"] = matches_info
		await self.send(
			text_data=json.dumps(basic_update)
		)


	async def group_game_state_update(self, event):
		# print("game_state:", " leon:", event["entity_data"]["leon"]["relativeY"], " local_opponent:", event["entity_data"]["local_opponent"]["relativeY"])
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

	from django.contrib.auth.models import User

	def create_data_collector(self, modus, username1, username2, matchName):
		try:
			user1 = User.objects.get(username=username1)
			user2 = User.objects.get(username=username2)
		except User.DoesNotExist:
			# Handle the case where one or both users don't exist
			raise ValueError("One or both users do not exist.")

		return GameDataCollector(user1=user1, user2=user2, matchName=matchName, type=modus)

	
	#i dont think we need a lock here, as we work with the instances own game_data
	#every instance has its own game_data
	#when an update happens, all game_datas are updated
	#here we could import the game from another file to keep things separated
	async def game_loop(self, modus):
		players = list(self.match.game_data.keys())
		if modus == 'remote' or modus == 'ai':
			players = list(self.match.game_data.keys())
			self.gdc = await sync_to_async(self.create_data_collector)(modus, players[0], players[1], self.match.group_name)
		if modus == 'local':
			self.gdc = await sync_to_async(self.create_data_collector)(modus, self.username, 'DUMP_LOCAL', self.match.group_name)
		logger.debug("new game loop started")
		pong_instance = Pong(self.gdc)
		FPS = 60
		iteration_time = 1 / FPS
		if modus == "ai":
			ai = AIPongOpponent(
				pong_instance.rightPaddle.y,
				pong_instance.rightPaddle.x,
				pong_instance.ball.x,
				pong_instance.ball.y,
				pong_instance.ball.dx,
				pong_instance.ball.dy,
				pong_instance.rightPaddle.dy,
				pong_instance.rightPaddle.height,
				iteration_time,
				10)
			ai_refresh_timer = time.time()
		should_run = True
		while should_run:
			if modus == "ai":
				if (time.time() - ai_refresh_timer >= 1):
					ai.setGameState(
						pong_instance.rightPaddle.y,
						pong_instance.rightPaddle.x,
						pong_instance.ball.x,
						pong_instance.ball.y,
						pong_instance.ball.dx,
						pong_instance.ball.dy,
						pong_instance.rightPaddle.dy,
						pong_instance.rightPaddle.height)
					ai_refresh_timer = time.time()
				ai_decision = ai.getAIDecision()
				self.match.game_data["AI_Ursula"]["direction"] = ai_decision

			#update entities with the iteration_time and keypresses
			entity_data = await pong_instance.update_entities(iteration_time, self.match.game_data)
			should_run = not entity_data["game_over"]
			#send all entity data to clients, so they can render the game
			# print(entity_data)
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "group_game_state_update", "entity_data": entity_data},
			)
			await asyncio.sleep(iteration_time)

		#remove player from registred after match, so the player can play again
		#also remove the match from the lobby and update the lobby
		if (modus == 'remote'):
			self.lobby.delete_match(str(self.match.group_name))
			self.lobby.remove_registered_player(players[0])
			self.lobby.remove_registered_player(players[1])
			await self.channel_layer.group_send(
					"lobby",
					{"type" : "group_lobby_update"},
			)

		#redirect the player to the game site
