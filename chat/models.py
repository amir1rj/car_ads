from account.models import User
from django.db import models


# Create your models here.
class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

    def last_messages(self):
        return Message.objects.order_by('-timestamp').all()

    def __str__(self):
        return self.author.username