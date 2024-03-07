from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asyncio import Lock
import json
import asyncio
from asgiref.sync import sync_to_async

WIDTH = 600
HEIGHT = 400
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60

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

class PongConsumer(AsyncWebsocketConsumer):
    ready   = False
    lock = Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = GameState()

    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # send the initial game state to the client (only one not the entire group/channel)
        await self.send(text_data=json.dumps({
            'leftPaddleY': self.game_state.leftPaddleY,
            'rightPaddleY': self.game_state.rightPaddleY,
            'ballX': self.game_state.ballX,
            'ballY': self.game_state.ballY,
            'scorePlayerLeft': self.game_state.scorePlayerLeft,
            'scorePlayerRight': self.game_state.scorePlayerRight
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
                self.game_state.leftPaddleY = leftPaddleY
            if rightPaddleY is not None:
                self.game_state.rightPaddleY = rightPaddleY

            #Update player state
            if ready is not None:
                self.ready = ready

            # If both players are ready, start the game
            if self.ready is True:
                # Update the game state with the received paddle positions
                if leftPaddleY is not None:
                    self.game_state.leftPaddleY = leftPaddleY
                if rightPaddleY is not None:
                    self.game_state.rightPaddleY = rightPaddleY

                # Update the ball position
                self.game_state.update_ball_position()

                # Send the updated game state to the client
                await self.send(text_data=json.dumps({
                    'leftPaddleY': self.game_state.leftPaddleY,
                    'rightPaddleY': self.game_state.rightPaddleY,
                    'ballX': self.game_state.ballX,
                    'ballY': self.game_state.ballY,
                    'scorePlayerLeft': self.game_state.scorePlayerLeft,
                    'scorePlayerRight': self.game_state.scorePlayerRight
                }))