from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asyncio import Lock
import json
import asyncio

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

WIDTH = 600
HEIGHT = 400
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60

import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GameState:
    def __init__(self):
        self.leftPaddleY = HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.rightPaddleY = HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.scorePlayerLeft = 0
        self.scorePlayerRight = 0
        self.ball_reset()

    def ball_reset(self):
        self.ballX = WIDTH / 2
        self.ballY = HEIGHT / 2
        self.ballSpeedX = 2
        self.ballSpeedY = 2

    def update_ball_position(self):
        self.ballX += self.ballSpeedX
        self.ballY += self.ballSpeedY

        # Bounce the ball off the top and bottom of the screen
        if self.ballY < 0 or self.ballY > HEIGHT:
            self.ballSpeedY = -self.ballSpeedY

        # Bounce the ball off the paddles
        if (self.ballX <= PADDLE_WIDTH and self.ballY >= self.leftPaddleY and self.ballY <= self.leftPaddleY + PADDLE_HEIGHT) or \
            (self.ballX >= (WIDTH - PADDLE_WIDTH) and self.ballY >= self.rightPaddleY and self.ballY <= self.rightPaddleY + PADDLE_HEIGHT):
            self.ballSpeedX = -self.ballSpeedX

        # Reset the ball if it goes out of bounds
        if self.ballX < 0:
            self.scorePlayerRight += 1
            self.ball_reset()
        if self.ballX > WIDTH:
            self.scorePlayerLeft += 1
            self.ball_reset()

# Create a single instance of the game state
game_state = GameState()
channel_layer = get_channel_layer()

class PongConsumer(AsyncWebsocketConsumer):
    client_id = 0
    ready   = False
    ready_clients = 0
    lock = Lock()

    async def connect(self):
        self.room_group_name = 'pong_group'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        PongConsumer.client_id += 1
        self.client_id = PongConsumer.client_id

        await self.send(text_data=json.dumps({
            'client_id': self.client_id
        }))

        # Send the initial game state to the client
        await self.send(text_data=json.dumps({
            'leftPaddleY': game_state.leftPaddleY,
            'rightPaddleY': game_state.rightPaddleY,
            'ballX': game_state.ballX,
            'ballY': game_state.ballY,
            'scorePlayerLeft': game_state.scorePlayerLeft,
            'scorePlayerRight': game_state.scorePlayerRight
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        leftPaddleY = text_data_json.get('leftPaddleY')
        rightPaddleY = text_data_json.get('rightPaddleY')
        ready = text_data_json.get('ready')

        # Update the game state with the received paddle positions
        async with PongConsumer.lock:
            if leftPaddleY is not None:
                game_state.leftPaddleY = leftPaddleY
            if rightPaddleY is not None:
                game_state.rightPaddleY = rightPaddleY

            #Update player state
            if ready is not None:
                self.ready = ready
                PongConsumer.ready_clients += 1

            # # If both players are ready, start the game
            # if PongConsumer.ready_clients == 2:  # Add this line
            #     # Update the game state with the received paddle positions
            #     if leftPaddleY is not None:
            #         game_state.leftPaddleY = leftPaddleY
            #     if rightPaddleY is not None:
            #         game_state.rightPaddleY = rightPaddleY

            #     # Update the ball position
            #     game_state.update_ball_position()

            #     # Send the updated game state to the client
            #     await self.send(text_data=json.dumps({
            #         'leftPaddleY': game_state.leftPaddleY,
            #         'rightPaddleY': game_state.rightPaddleY,
            #         'ballX': game_state.ballX,
            #         'ballY': game_state.ballY,
            #         'scorePlayerLeft': game_state.scorePlayerLeft,
            #         'scorePlayerRight': game_state.scorePlayerRight
            #     }))
    async def send_game_state(self, event):
        # Send the game state to the client
        await self.send(text_data=json.dumps(event))

async def update_game_state():
    while True:
        # Update the ball position
        game_state.update_ball_position()
        logger.info('This is a log message.')


        # Send the updated game state to the client
        await channel_layer.group_send(
            'pong_group',
            {
                'type': 'send_game_state',
                'leftPaddleY': game_state.leftPaddleY,
                'rightPaddleY': game_state.rightPaddleY,
                'ballX': game_state.ballX,
                'ballY': game_state.ballY,
                'scorePlayerLeft': game_state.scorePlayerLeft,
                'scorePlayerRight': game_state.scorePlayerRight
            }
        )

        await asyncio.sleep(0.01)

application = ProtocolTypeRouter({
    # ...
    'websocket': URLRouter([
        path('ws/pong/', PongConsumer.as_asgi()),
    ]),
    'background': update_game_state,
})