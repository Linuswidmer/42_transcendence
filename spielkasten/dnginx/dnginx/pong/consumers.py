# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer

class WebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        
        # Send a "Hello, world!" message to the client
        await self.send(text_data="Hello, world!")

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass
