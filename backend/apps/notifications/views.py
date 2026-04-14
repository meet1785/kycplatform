from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """List user notifications."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["channel", "status", "is_read"]
    ordering_fields = ["created_at"]

    @extend_schema(tags=["Notifications"])
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationReadView(APIView):
    """Mark a notification as read."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Notifications"])
    def patch(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.status = Notification.STATUS_READ
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "status", "read_at"])
            return Response(NotificationSerializer(notification).data)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class MarkAllNotificationsReadView(APIView):
    """Mark all notifications as read."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Notifications"])
    def post(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(
            is_read=True,
            status=Notification.STATUS_READ,
            read_at=timezone.now(),
        )
        return Response({"detail": f"Marked {count} notifications as read."})
