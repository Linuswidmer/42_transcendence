import json
import uuid
import asyncio
import time
import logging

from adjectiveanimalnumber import generate

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
			success, message = self.lobby.register_player_match(
				self.username, match_id
			)
			if success:
				self.game_group_name = match_id
				
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
			success, message = self.lobby.join(self.username, json_from_client["match_id"])
			if success:
				await self.join_remote_game(match_id)
				return None
			else:
				json_from_client["error"] = message
		
		if action == "join" and modus == "local":
			await self.join_local_game()
			return None
			
		if action == "join" and modus == "ai":
			await self.join_ai_game()
			return None
		
		json_from_client["type"] = "group_lobby_update"
		return json_from_client


	async def join_ai_game(self):
		self.in_game = True
		self.hosts_game = True
		self.game_group_name = "ai"

		self.game_data[self.username] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
		
		self.game_data["ai_opponent"] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
					
		await self.channel_layer.group_add(
			self.game_group_name, self.channel_name
		)

		await self.send(text_data=json.dumps({"type": "join", "modus": "ai"}))

	async def join_local_game(self):
		self.in_game = True
		self.hosts_game = True
		self.game_group_name = "local"

		self.game_data[self.username] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
		
		self.game_data["local_opponent"] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
					
		await self.channel_layer.group_add(
			self.game_group_name, self.channel_name
		)

		await self.send(text_data=json.dumps({"type": "join", "modus": "local"}))

	async def join_remote_game(self, match_id):
		self.in_game = True
		if self.lobby.should_host_game(self.username, match_id):
			self.hosts_game = True
		match = self.lobby.get_match(match_id)
		# match.modus = modus
		players = match.get_registered_players()
		for player in players:
			self.game_data[player] = {
				"score": 0,
				"moveUp": False,
				"moveDown": False,
				"direction": 0,
				}
		
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
	async def game_loop(self, modus):
		logger.debug("new game loop started")
		pong_instance = Pong()
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
		while 1:
			# start_time = time.time()
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
				self.game_data["ai_opponent"]["direction"] = ai_decision


			#update entities with the iteration_time and keypresses
			entity_data = pong_instance.update_entities(iteration_time, self.game_data)

			#send all entity data to clients, so they can render the game
			await self.channel_layer.group_send(
				self.game_group_name,
				{"type": "group_game_state_update", "entity_data": entity_data},
			)
			await asyncio.sleep(iteration_time)

			# end_time = time.time()  # End time of the iteration
			# iteration_time_measured = end_time - start_time
			# margin = 0.1
			# if iteration_time_measured  > (iteration_time * (1 + margin)):
			# 	print("Warning: Server cannot keep up with the desired framerate.", iteration_time_measured, ">", iteration_time)
