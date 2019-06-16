import json
from enum import Enum

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class MessageType(Enum):
    ERROR = 0,
    WARNING = 1,
    INFO = 2,
    SUCCESS = 3


class LogConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope['user'].is_superuser:
            return

        self.log_var = self.scope['url_route']['kwargs']['log_var']
        async_to_sync(self.channel_layer.group_add)(self.log_var, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.log_var, self.channel_name)

    def receive(self, text_data, bytes_data):
        pass

    def log_event(self, event):
        self.send(json.dumps({'level': event['level'], 'message': event['message']}))
