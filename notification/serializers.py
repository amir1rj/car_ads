from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """

    class Meta:
        model = Notification
        fields = ['id', 'message', 'message_type', 'created_at', 'is_read']
