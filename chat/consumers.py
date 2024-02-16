import base64
import json
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer

from account.models import User
from account.utils import check_message
from chat.models import Message, Chat, Chat_Image
from chat.serializers import MessageSerializer

from rest_framework.renderers import JSONRenderer


class ChatConsumer(WebsocketConsumer):
    def new_message(self, data, ):
        username, message, roomName = data.get('username'), data.get('content'), data.get('roomName')
        username_model = User.objects.get(username=username)
        chat_model = Chat.objects.filter(roomName=roomName).first()
        message_model = Message.objects.create(author=username_model, content=message, chat=chat_model)
        content = eval(self.messgeSeialization(message_model))
        validated_content = check_message(content)
        result = {
            "content": validated_content,
            "username": username,
            "command": "new_message"
        }

        self.send_to_chat_message(result)

    def fetch_message(self, data):
        roomName = data["roomName"]
        qs = Message.last_messages(self, roomName)
        message_json = self.messgeSeialization(qs)
        content = {
            "message": eval(message_json),
            "command": "fetch_message",
        }
        self.chat_message(content)

    def image(self, data):
        pass

    commands = {

        "new_message": new_message,
        "fetch_message": fetch_message,
        "img": image,

    }

    # @database_sync_to_asyn
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
        command = text_data_json.get('command')
        print(text_data_json)
        self.commands[command](self, text_data_json)
        # Send message to room group

    def send_to_chat_message(self, message, ):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "chat.message", "message": message.get('content'), "command": message.get('command'),
                "username": message.get('username'),
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
# @database_sync_to_async
# def get_user_model(self, username):
#     return User.objects.filter(user__username=username).first()
#
# @database_sync_to_async
# def get_chat_model(self, roomName):
#     return Chat.objects.filter(roomName=roomName).first()
