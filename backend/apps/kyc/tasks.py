import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_kyc_verification(self, application_id):
    """
    Background task to process KYC verification via provider API.
    """
    from apps.kyc.models import KYCApplication
    from apps.kyc.services import process_kyc_with_provider, update_kyc_status
    from apps.notifications.tasks import send_kyc_status_notification

    try:
        application = KYCApplication.objects.get(id=application_id)
    except KYCApplication.DoesNotExist:
        logger.error(f"KYC application {application_id} not found.")
        return

    try:
        success, provider_ref, provider_status, score = process_kyc_with_provider(application)

        if provider_ref:
            application.kyc_provider_ref = provider_ref
            application.kyc_provider_status = provider_status
            application.kyc_score = score
            application.save(update_fields=["kyc_provider_ref", "kyc_provider_status", "kyc_score"])

        if success and provider_status == "approved":
            new_status = KYCApplication.STATUS_APPROVED
        elif success and provider_status == "review_required":
            # Leave in processing for manual review
            new_status = KYCApplication.STATUS_PROCESSING
        else:
            new_status = KYCApplication.STATUS_REJECTED

        update_kyc_status(
            application,
            new_status,
            reason="Automatic verification failed." if new_status == KYCApplication.STATUS_REJECTED else "",
        )

        # Notify user via WebSocket and notifications
        send_kyc_status_notification.delay(str(application.user.id), new_status)

        # Send WebSocket notification
        _notify_kyc_update(str(application.user.id), new_status, str(application.id))

        logger.info(f"KYC verification completed for {application_id}: {new_status}")

    except Exception as exc:
        logger.error(f"KYC verification task failed for {application_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_kyc_reminder(self, user_id):
    """Send reminder to users who haven't completed KYC."""
    from django.contrib.auth import get_user_model
    from apps.kyc.models import KYCApplication
    from apps.notifications.services import NotificationService

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        application = KYCApplication.objects.filter(
            user=user,
            status__in=[KYCApplication.STATUS_PENDING, KYCApplication.STATUS_RESUBMIT],
        ).first()

        if application:
            NotificationService.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject="Complete your KYC verification",
                message="Please complete your KYC verification to access all features.",
            )
            logger.info(f"KYC reminder sent to {user.email}")
    except Exception as exc:
        logger.error(f"KYC reminder task failed for {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_documents():
    """Clean up expired signed URLs."""
    from apps.kyc.models import KYCDocument

    expired = KYCDocument.objects.filter(
        signed_url_expires_at__lt=timezone.now()
    ).exclude(signed_url="")
    count = expired.update(signed_url="", signed_url_expires_at=None)
    logger.info(f"Cleaned up {count} expired document signed URLs.")


def _notify_kyc_update(user_id, status, application_id):
    """Send WebSocket notification for KYC status update."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "kyc_update",
                    "data": {
                        "application_id": application_id,
                        "status": status,
                        "timestamp": timezone.now().isoformat(),
                    },
                },
            )
    except Exception as e:
        logger.error(f"WebSocket notification failed for user {user_id}: {e}")
