# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from account.models import User
from chat.models import Message
from chat.serializers import MessageSerializer

from rest_framework.renderers import JSONRenderer


class ChatConsumer(WebsocketConsumer):
    def new_message(self, message, username, ):
        username_model = User.objects.get(username=username)
        message_model = Message.objects.create(author=username_model, content=message)

        result = self.messgeSeialization(message_model)

        self.send_to_chat_message(eval(result))

    def fetch_message(self, message=None, username=None):
        qs = Message.last_messages(self)

        message_json = self.messgeSeialization(qs)
        content = {
            "message": eval(message_json),
            "command": "fetch_message",

        }

        self.chat_message(content)

    commands = {

        "new_message": new_message,
        "fetch_message": fetch_message,

    }

    def messgeSeialization(self, qs):
        serialized = MessageSerializer(qs,
                                       many=(lambda qs: True if (qs.__class__.__name__ == 'QuerySet') else False)(qs))
        content = JSONRenderer().render(serialized.data)
        return content

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        command = text_data_json.get('command')
        username = text_data_json.get('username')

        self.commands[command](self, message, username)
        # Send message to room group

    def send_to_chat_message(self, message, ):
        print("salammmmmmmmmmm")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "chat.message",
                "message": message,
                "command": "new_message"
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
