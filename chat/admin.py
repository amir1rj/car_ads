from django.contrib import admin

from chat.models import Message


# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["content",'__str__','timestamp']
    list_filter = ["timestamp"]