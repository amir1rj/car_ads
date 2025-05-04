from django_filters import FilterSet
from notification.models import Notification


class NotificationFilter(FilterSet):
    class Meta:
        model = Notification
        fields = ['message_type']
