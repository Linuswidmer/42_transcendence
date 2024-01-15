from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        pass

    # Handle messages from WebSocket
async def receive(self, text_data):
    text_data_json = json.loads(text_data)
    leftPaddleY = text_data_json['leftPaddleY']
    rightPaddleY = text_data_json['rightPaddleY']

    printf(f'receiving message')
    print(f'Left paddle Y: {leftPaddleY}, Right paddle Y: {rightPaddleY}')

    # Do something with the paddle positions...
    # For now, just echo them back to the client
    await self.send(text_data=json.dumps({
        'leftPaddleY': leftPaddleY,
        'rightPaddleY': rightPaddleY
    }))