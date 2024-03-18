# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

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