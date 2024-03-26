from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Profile

class OnlineStatusConsumer(AsyncWebsocketConsumer):
      async def connect(self):
            # Access the user from the scope
            user = self.scope.get('user')

            # Check if the user is authenticated
            if user.is_authenticated:
            # Update the user's is_logged_in field to True
                  await self.update_user_logged_in(user, True)

            # Other connection setup logic goes here
            await self.accept()

      async def disconnect(self, close_code):
            # Access the user from the scope
            user = self.scope.get('user')

            # Check if the user is authenticated
            if user.is_authenticated:
            # Update the user's is_logged_in field to False
                  await self.update_user_logged_in(user, False)

            # Perform cleanup tasks on disconnect
            pass

      @database_sync_to_async
      def update_user_logged_in(self, user, is_logged_in):
            # Update the user's is_logged_in field
            user.profile.is_logged_in = is_logged_in
            user.profile.save()