from django.db.models import Q
import uuid
from django.utils.text import slugify
from chat.models import Chat
from django.db import transaction


def generate_unique_room_name():
    return str(uuid.uuid4()).replace("-", "")


@transaction.atomic
def get_or_create_chat_with_users(user1, user2):
    # chat = Chat.objects.filter(Q(users__id=user2.id)).first()
    chat = Chat.objects.filter(users=user1).filter(Q(users=user2)).first()
    if chat is None:
        chat = Chat.objects.create(roomName=generate_unique_room_name())
        chat.save()
        chat.users.add(user1, user2)
    return chat
