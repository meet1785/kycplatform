from django.urls import path
from apps.notifications.views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications"),
    path("<uuid:notification_id>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
    path("mark-all-read/", MarkAllNotificationsReadView.as_view(), name="notifications-mark-all-read"),
]
