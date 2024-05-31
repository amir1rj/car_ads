from rest_framework import serializers
from account.models import User, Profile
from chat.models import Message, Chat
from account.serializers import ProfileSerializer


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['__str__', 'content', 'timestamp']

class ChatSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'roomName', 'users', 'profile')

    def get_profile(self, obj):
        # دریافت لیست کاربران
        users = obj.users.all()
        # دریافت اطلاعات کاربر از request
        current_user = self.context['request'].user
        user = users.exclude(pk=current_user.pk).first()

        profile_serializer = ProfileListSerializer(instance=user.profile)

        return profile_serializer.data


class UserSerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'chats')
