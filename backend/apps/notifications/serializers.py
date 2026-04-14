from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "channel", "subject", "message", "status",
            "is_read", "created_at", "sent_at", "read_at",
        ]
        read_only_fields = fields
