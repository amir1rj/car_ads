from account.models import User
from notification.models import Notification, BroadcastNotification


def send_personal_notification(user, message, message_type='custom'):
    """
    Send a personal notification to a specific user.

    :param user: User instance to send the notification to
    :param message: The message content
    :param message_type: The type of message (default: 'custom')
    """
    Notification.objects.create(
        recipient=user,
        message=message,
        message_type=message_type
    )


def send_broadcast_notification(message):
    """
    Send a broadcast notification to all users.

    :param message: The message content
    """
    # Save the broadcast in a separate model
    BroadcastNotification.objects.create(message=message)

    # Send the notification to all users
    users = User.objects.all()
    for user in users:
        Notification.objects.create(
            recipient=user,
            message=message,
            message_type='broadcast'
        )
