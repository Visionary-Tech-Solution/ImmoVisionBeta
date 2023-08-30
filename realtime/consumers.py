import json,jwt
from channels.generic.websocket import WebsocketConsumer
from authentication.models import User

from asgiref.sync import async_to_sync

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        
        # Authenticate the user and create a group for the user
        # data = self.scope.get('headers')
        # print(data)
        # email = None
        # for key,value in data:
        #     if key == b'email':
        #         email=value.decode('utf-8')
        #         self.email = email
        # print(f"Your email is ====>{email}")
        
        
        async_to_sync(self.channel_layer.group_add)(
            f"user_", self.channel_name
        )
        self.accept()
        

    def disconnect(self, close_code):
        # Remove the user from the group when disconnecting
       pass

    def send_notification(self, event):
        # Send notification to the user's group
        notification = event['notification']
        self.send(text_data=json.dumps(notification))