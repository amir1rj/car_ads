from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .filters import NotificationFilter
from .models import Notification, BroadcastNotification
from .serializers import NotificationSerializer
from django.contrib.auth.models import User
from rest_framework.decorators import action


@extend_schema(
    tags=['Notifications'],
    parameters=[
        OpenApiParameter(
            name='message_type',
            description='Filter notifications by type',
            required=False,
            type=str,
            enum=[choice[0] for choice in Notification.MESSAGE_TYPE_CHOICES]
        )
    ]
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for retrieving and marking notifications as read for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

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
