import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class TwilioSMSService:
    """Send SMS notifications via Twilio."""

    @staticmethod
    def send(to_number, message):
        """Send SMS message. Returns (success, message_sid)."""
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number,
            )
            logger.info("SMS sent successfully, SID: %s", msg.sid)
            return True, msg.sid
        except Exception as e:
            logger.error("SMS send failed: %s", type(e).__name__)
            return False, "SMS delivery failed"


class TwilioWhatsAppService:
    """Send WhatsApp notifications via Twilio."""

    @staticmethod
    def send(to_number, message):
        """Send WhatsApp message. Returns (success, message_sid)."""
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            whatsapp_from = settings.TWILIO_WHATSAPP_NUMBER
            whatsapp_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number

            msg = client.messages.create(
                body=message,
                from_=whatsapp_from,
                to=whatsapp_to,
            )
            logger.info("WhatsApp message sent successfully, SID: %s", msg.sid)
            return True, msg.sid
        except Exception as e:
            logger.error("WhatsApp send failed: %s", type(e).__name__)
            return False, "WhatsApp delivery failed"


class BrevoEmailService:
    """Send transactional emails via Brevo (Sendinblue)."""

    @staticmethod
    def send(to_email, to_name, subject, message, html_content=None):
        """Send email. Returns (success, message_id)."""
        try:
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException

            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY

            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={"name": settings.DEFAULT_FROM_NAME, "email": settings.DEFAULT_FROM_EMAIL},
                subject=subject,
                text_content=message,
                html_content=html_content or f"<p>{message}</p>",
            )

            result = api_instance.send_transac_email(send_smtp_email)
            logger.info("Email sent successfully, message_id: %s", result.message_id)
            return True, result.message_id
        except Exception as e:
            logger.error("Email send failed: %s", type(e).__name__)
            return False, "Email delivery failed"


class NotificationService:
    """Unified notification service."""

    @staticmethod
    def send_sms(user, message):
        """Send SMS to a user."""
        from apps.notifications.models import Notification

        notification = Notification.objects.create(
            user=user,
            channel=Notification.CHANNEL_SMS,
            message=message,
        )

        if not user.phone_number:
            notification.status = Notification.STATUS_FAILED
            notification.error_message = "User has no phone number."
            notification.save(update_fields=["status", "error_message"])
            return False

        success, ref = TwilioSMSService.send(user.phone_number, message)
        notification.status = Notification.STATUS_SENT if success else Notification.STATUS_FAILED
        notification.provider_message_id = ref if success else ""
        notification.error_message = "" if success else ref
        notification.sent_at = timezone.now() if success else None
        notification.save()
        return success

    @staticmethod
    def send_whatsapp(user, message):
        """Send WhatsApp message to a user."""
        from apps.notifications.models import Notification

        notification = Notification.objects.create(
            user=user,
            channel=Notification.CHANNEL_WHATSAPP,
            message=message,
        )

        if not user.phone_number:
            notification.status = Notification.STATUS_FAILED
            notification.error_message = "User has no phone number."
            notification.save(update_fields=["status", "error_message"])
            return False

        success, ref = TwilioWhatsAppService.send(user.phone_number, message)
        notification.status = Notification.STATUS_SENT if success else Notification.STATUS_FAILED
        notification.provider_message_id = ref if success else ""
        notification.error_message = "" if success else ref
        notification.sent_at = timezone.now() if success else None
        notification.save()
        return success

    @staticmethod
    def send_email(to_email, to_name, subject, message, html_content=None):
        """Send email notification."""
        from django.contrib.auth import get_user_model
        from apps.notifications.models import Notification

        User = get_user_model()
        try:
            user = User.objects.get(email=to_email)
        except User.DoesNotExist:
            user = None

        if user:
            notification = Notification.objects.create(
                user=user,
                channel=Notification.CHANNEL_EMAIL,
                subject=subject,
                message=message,
            )

        success, ref = BrevoEmailService.send(to_email, to_name, subject, message, html_content)

        if user:
            notification.status = Notification.STATUS_SENT if success else Notification.STATUS_FAILED
            notification.provider_message_id = ref if success else ""
            notification.error_message = "" if success else ref
            notification.sent_at = timezone.now() if success else None
            notification.save()

        return success
