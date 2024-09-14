from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification, BroadcastNotification
from .serializers import NotificationSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import action


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for retrieving and marking notifications as read for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only notifications that belong to the authenticated user.
        """
        return Notification.objects.filter(recipient=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a notification by ID and mark it as read.
        """
        notification = self.get_object()
        # Mark the notification as read
        if not notification.is_read:
            notification.is_read = True
            notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)
