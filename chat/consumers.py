
import json
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncJsonWebsocketConsumer
from account.models import User
from account.utils import check_message
from chat.models import Message, Chat, Chat_Image
from chat.serializers import MessageSerializer
from rest_framework.renderers import JSONRenderer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def new_message(self, data, ):
        username, message, roomName = data.get('username'), data.get('content'), data.get('roomName')

        user_model = await self.get_user_model(username)

        chat_model = await self.get_chat_modal(roomName)

        message_model = await self.create_message(author=user_model, content=message, chat=chat_model)

        content = await self.messgeSeialization(message_model)

        validated_content = check_message(content)
        result = {
            "content": validated_content,
            "command": "new_message",
            "roomName": roomName,
        }
        await self.send_to_chat_message(result)
        await self.notif(result)

    @database_sync_to_async
    def fetch_message_qs(self, room_name):
        return Message.last_messages(self, room_name)

    async def fetch_message(self, data):
        roomName = data["roomName"]
        qs = await self.fetch_message_qs(roomName)
        message_json = await self.messgeSeialization(qs)
        content = {
            "message": message_json,
            "command": "fetch_message",
        }
        await self.chat_message(content)

    commands = {

        "new_message": new_message,
        "fetch_message": fetch_message,

    }

    @database_sync_to_async
    def create_message(self, author, content, chat):
        return Message.objects.create(author=author, content=content, chat=chat)

    @database_sync_to_async
    def get_user_model(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def get_chat_modal(self, room_name):
        return Chat.objects.filter(roomName=room_name).first()

    @database_sync_to_async
    def messgeSeialization(self, qs):
        serialized = MessageSerializer(qs,
                                       many=(lambda qs: True if (qs.__class__.__name__ == 'QuerySet') else False)(
                                           qs))
        content = JSONRenderer().render(serialized.data)
        return eval(content)

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def get_chat_members(self, room_name):
        members = Chat.objects.get(roomName=room_name).users.all()
        members_list = []
        for i in members:
            members_list.append(i.username)
        return members_list

    async def notif(self, data):
        members_list = await self.get_chat_members(data.get('roomName'))
        await self.channel_layer.group_send(
            'chat_listener',
            {
                'type': 'chat_message',
                'message': data.get("content"),
                'members_list': members_list,
                'roomName': data['roomName'],

            }
        )


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command')
        await self.commands[command](self, text_data_json)

    async def send_to_chat_message(self, message, ):
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat.message", "message": message.get('content'), "command": message.get('command'),
             
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
# @database_sync_to_async
# def get_user_model(self, username):
#     return User.objects.filter(user__username=username).first()
#
# @database_sync_to_async
# def get_chat_model(self, roomName):
#     return Chat.objects.filter(roomName=roomName).first()
