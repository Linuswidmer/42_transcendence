from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ballX = 300
        self.ballY = 200
        self.ballSpeedX = 2
        self.ballSpeedY = 2
        self.leftPaddleY = 0
        self.rightPaddleY = 0

    def update_ball_position(self):
        self.ballX += self.ballSpeedX
        self.ballY += self.ballSpeedY

        # Bounce the ball off the top and bottom of the screen
        if self.ballY < 0 or self.ballY > 400:  # Assuming canvas height is 400
            self.ballSpeedY = -self.ballSpeedY

        # Bounce the ball off the paddles
        if (self.ballX <= 10 and self.ballY >= self.leftPaddleY and self.ballY <= self.leftPaddleY + 60) or \
            (self.ballX >= 590 and self.ballY >= self.rightPaddleY and self.ballY <= self.rightPaddleY + 60):
            self.ballSpeedX = -self.ballSpeedX

        # Reset the ball if it goes out of bounds
        if self.ballX < 0 or self.ballX > 600:  # Assuming canvas width is 600
            self.reset()

# Create a single instance of the game state
game_state = GameState()

class PongConsumer(WebsocketConsumer):
    client_id = 0
    ready = False
    ready_clients = 0

    def connect(self):
        self.room_group_name = 'pong_group'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        PongConsumer.client_id += 1
        self.client_id = PongConsumer.client_id

        self.send(text_data=json.dumps({
            'client_id': self.client_id
        }))

        # Send the initial game state to the client
        self.send(text_data=json.dumps({
            'leftPaddleY': game_state.leftPaddleY,
            'rightPaddleY': game_state.rightPaddleY,
            'ballX': game_state.ballX,
            'ballY': game_state.ballY
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        leftPaddleY = text_data_json.get('leftPaddleY')
        rightPaddleY = text_data_json.get('rightPaddleY')
        ready = text_data_json.get('ready')

        # Update the game state with the received paddle positions
        if leftPaddleY is not None:
            game_state.leftPaddleY = leftPaddleY
        if rightPaddleY is not None:
            game_state.rightPaddleY = rightPaddleY

        #Update player state
        if ready is not None:
            self.ready = ready
            PongConsumer.ready_clients += 1

        # If both players are ready, start the game
        if PongConsumer.ready_clients == 2:  # Add this line
            # Update the game state with the received paddle positions
            if leftPaddleY is not None:
                game_state.leftPaddleY = leftPaddleY
            if rightPaddleY is not None:
                game_state.rightPaddleY = rightPaddleY

            # Update the ball position
            game_state.update_ball_position()

            # Send the updated game state to the client
            self.send(text_data=json.dumps({
                'leftPaddleY': game_state.leftPaddleY,
                'rightPaddleY': game_state.rightPaddleY,
                'ballX': game_state.ballX,
                'ballY': game_state.ballY
            }))