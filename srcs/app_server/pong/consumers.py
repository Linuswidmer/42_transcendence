# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asyncio import Lock
import json
import asyncio
from asgiref.sync import sync_to_async

from .GameData import GameData

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
        self.game_over = False

        self.game_data = GameData('Linus', 'Alex', 'local') # instance of game data

    def ball_reset(self):
        self.ballX = WIDTH / 2
        self.ballY = HEIGHT / 2
        self.ballSpeedX = 2
        self.ballSpeedY = 2

    def is_game_over(self):
        return self.game_over

    def update_ball_position(self):
        self.ballX += self.ballSpeedX
        self.ballY += self.ballSpeedY

        # Bounce the ball off the top and bottom of the screen
        if self.ballY < 0 or self.ballY > HEIGHT:
            self.ballSpeedY = -self.ballSpeedY

        # Bounce the ball off the paddles
        if (self.ballX <= PADDLE_WIDTH and self.ballY >= self.leftPaddleY and self.ballY <= self.leftPaddleY + PADDLE_HEIGHT):
            self.ballSpeedX = -self.ballSpeedX
            # update game data
            self.game_data.ballHit(True)

        elif (self.ballX >= (WIDTH - PADDLE_WIDTH) and self.ballY >= self.rightPaddleY and self.ballY <= self.rightPaddleY + PADDLE_HEIGHT):
            self.ballSpeedX = -self.ballSpeedX
            # update game data
            self.game_data.ballHit(False)

        # Reset the ball if it goes out of bounds
        if self.ballX < 0:
            self.scorePlayerRight += 1
            if self.scorePlayerRight == 3:
                self.game_over = True
            else:
                self.ball_reset()

            # update game data
            self.game_data.endRally(False)
        if self.ballX > WIDTH:
            self.scorePlayerLeft += 1
            if self.scorePlayerLeft == 3:
                self.game_over = True
            else:
                self.ball_reset()
            
            # update game data
            self.game_data.endRally(True)

# Create a single instance of the game state

class PongConsumer(AsyncWebsocketConsumer):
    ready   = False
    lock = Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = GameState()

    async def connect(self):
        self.room_group_name = 'test'
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

                if self.game_state.is_game_over():
                    # Send a game over message to the client
                    await self.send(text_data=json.dumps({
                        'gameOver': True,
                        'scorePlayerLeft': self.game_state.scorePlayerLeft,
                        'scorePlayerRight': self.game_state.scorePlayerRight
                    }))

                    # save and print GameData
                    self.game_state.game_data.endGame()
                    self.game_state.game_data.printData()

                    await self.close()
                else:
                    # Send the updated game state to the client
                    await self.send(text_data=json.dumps({
                        'leftPaddleY': self.game_state.leftPaddleY,
                        'rightPaddleY': self.game_state.rightPaddleY,
                        'ballX': self.game_state.ballX,
                        'ballY': self.game_state.ballY,
                        'scorePlayerLeft': self.game_state.scorePlayerLeft,
                        'scorePlayerRight': self.game_state.scorePlayerRight
                    }))


# ONLY FOR TESTING
class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join a group
        await self.channel_layer.group_add(
            "chat",
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            "chat",
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to group
        await self.channel_layer.group_send(
            "chat",
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))