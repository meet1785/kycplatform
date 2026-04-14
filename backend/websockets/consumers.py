import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class KYCConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time KYC status updates.
    Clients connect to ws://host/ws/kyc/ with a valid JWT token.
    """

    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.user_group = f"user_{self.user.id}"

        # Join user-specific group
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

        # Send connection confirmation
        await self.send(
            text_data=json.dumps({
                "type": "connection_established",
                "message": "Connected to KYC updates.",
                "user_id": str(self.user.id),
            })
        )
        logger.info(f"WebSocket connected: user={self.user.email}")

    async def disconnect(self, close_code):
        if hasattr(self, "user_group"):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        logger.info(f"WebSocket disconnected: code={close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))
            elif message_type == "get_kyc_status":
                kyc_data = await self.get_kyc_status()
                await self.send(text_data=json.dumps({"type": "kyc_status", "data": kyc_data}))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "Invalid JSON."}))

    async def kyc_update(self, event):
        """Handle KYC update events from channel layer."""
        await self.send(
            text_data=json.dumps({
                "type": "kyc_update",
                "data": event["data"],
            })
        )

    async def notification(self, event):
        """Handle general notification events."""
        await self.send(
            text_data=json.dumps({
                "type": "notification",
                "data": event["data"],
            })
        )

    @database_sync_to_async
    def get_kyc_status(self):
        """Get current KYC status for the user."""
        try:
            application = self.user.kyc_application
            return {
                "application_id": str(application.id),
                "status": application.status,
                "submitted_at": application.submitted_at.isoformat() if application.submitted_at else None,
                "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
            }
        except Exception:
            return {"status": "no_application"}
