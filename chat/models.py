from account.models import User
from django.db import models


# Create your models here.


class Chat(models.Model):
    roomName = models.CharField(max_length=50)
    # ad = models.ForeignKey(Add,,,,,)
    memeber = models.ManyToManyField(User, null=True, blank=True)

    def __str__(self):
        return self.roomName


class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    #  should remove blank and null property
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages",null=True,blank=True)


    def last_messages(self,roomName):
        return Message.objects.order_by('-timestamp').filter(chat__roomName=roomName)

    def __str__(self):
        return self.author.username
