from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from .models import Notification, BroadcastNotification
from .tasks import send_personal_notification, send_broadcast_notification
from django import forms
from account.models import User


class SendNotificationForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False,
                                       help_text="User for personal notification.")
    message = forms.CharField(widget=forms.Textarea, help_text="Message content.")
    is_broadcast = forms.BooleanField(required=False, help_text="Check this to send a broadcast message to all users.")


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'message_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message', 'message_type')
    list_filter = ('is_read', 'message_type')

    actions = ['send_notification']

    def send_notification(self, request, queryset=None):
        """
        Custom admin action to send notifications.
        """
        if 'apply' in request.POST:
            form = SendNotificationForm(request.POST)
            if form.is_valid():
                recipient = form.cleaned_data['recipient']
                message = form.cleaned_data['message']
                is_broadcast = form.cleaned_data['is_broadcast']

                if is_broadcast:
                    send_broadcast_notification(message)
                    self.message_user(request, "Broadcast notification sent successfully", level=messages.SUCCESS)
                else:
                    if recipient:
                        send_personal_notification(recipient, message)
                        self.message_user(request, "Personal notification sent successfully", level=messages.SUCCESS)
                    else:
                        self.message_user(request, "Recipient is required for personal notifications",
                                          level=messages.ERROR)
            else:
                self.message_user(request, "Invalid form", level=messages.ERROR)
            return

        form = SendNotificationForm()
        return admin.helpers.AdminForm(request, form)

    send_notification.short_description = "Send notification"


admin.site.register(Notification, NotificationAdmin)


@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'message_summary']
    search_fields = ['message']
    readonly_fields = ['created_at']
    actions = ['send_broadcast_notification']

    def message_summary(self, obj):
        """
        Displays a truncated version of the message in the admin list.
        """
        return format_html(f"{obj.message[:50]}...") if len(obj.message) > 50 else obj.message

    message_summary.short_description = 'Message Summary'

    def send_broadcast_notification(self, request, queryset):
        """
        Action to send the selected broadcast notifications to all users.
        """
        for broadcast in queryset:
            # Logic to send the broadcast message to all users
            users = User.objects.values_list('id', flat=True)  # Optimized query for bulk operations
            notifications = [Notification(recipient_id=user_id, message=broadcast.message, message_type='broadcast') for
                             user_id in users]
            Notification.objects.bulk_create(notifications)
        self.message_user(request, "Broadcast notification(s) sent successfully.")

    send_broadcast_notification.short_description = "Send selected broadcast notifications to all users"
