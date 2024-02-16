from rest_framework import serializers
from account.models import User
from chat.models import Message, Chat


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['__str__', 'content', 'timestamp']


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ('id', 'roomName', 'users')


class UserSerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'chats')
