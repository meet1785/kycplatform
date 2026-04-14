from django.contrib import admin
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "channel", "subject", "status", "is_read", "created_at", "sent_at"]
    list_filter = ["channel", "status", "is_read"]
    search_fields = ["user__email", "subject", "message"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "sent_at", "read_at"]
