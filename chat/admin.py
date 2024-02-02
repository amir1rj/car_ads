from django.contrib import admin

from chat.models import Message, Chat, Chat_Image


# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["content",'__str__','timestamp']
    list_filter = ["timestamp"]

admin.site.register(Chat)
admin.site.register(Chat_Image)
