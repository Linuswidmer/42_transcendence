from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class PongConsumer(WebsocketConsumer):
    client_id = 0

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

        # Initialize ball properties
        self.ballX = 400  # Half of canvas width
        self.ballY = 300  # Half of canvas height
        self.ballSpeedX = 2
        self.ballSpeedY = 2

        # Initialize paddle properties
        self.leftPaddleY = 0
        self.rightPaddleY = 0

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        PongConsumer.client_id -= 1

    # Update ball position
    def update_ball_position(self):
        self.ballX += self.ballSpeedX
        self.ballY += self.ballSpeedY

        # Bounce the ball off the top and bottom of the screen
        if self.ballY < 0 or self.ballY > 400:  # Assuming canvas height is 600
            self.ballSpeedY = -self.ballSpeedY

        # Bounce the ball off the paddles
        # You would need to add the necessary logic here based on your game rules
        if (self.ballX <= 10 and self.ballY >= self.leftPaddleY and self.ballY <= self.leftPaddleY + 60) or \
            (self.ballX >= 590 and self.ballY >= self.rightPaddleY and self.ballY <= self.rightPaddleY + 60):
            self.ballSpeedX = -self.ballSpeedX

    # Handle messages from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        leftPaddleY = text_data_json.get('leftPaddleY')
        rightPaddleY = text_data_json.get('rightPaddleY')

        # Update paddle positions only if they are included in the received data
        if leftPaddleY is not None:
            self.leftPaddleY = leftPaddleY
        if rightPaddleY is not None:
            self.rightPaddleY = rightPaddleY

        # Update ball position
        self.update_ball_position()

        # Send the updated paddle and ball positions to all clients
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_positions',
                'leftPaddleY': self.leftPaddleY,
                'rightPaddleY': self.rightPaddleY,
                'ballX': self.ballX,
                'ballY': self.ballY
            }
        )

    # Handle 'game_positions' events
    def game_positions(self, event):
        leftPaddleY = event['leftPaddleY']
        rightPaddleY = event['rightPaddleY']
        ballX = event['ballX']
        ballY = event['ballY']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'leftPaddleY': leftPaddleY,
            'rightPaddleY': rightPaddleY,
            'ballX': ballX,
            'ballY': ballY
        }))