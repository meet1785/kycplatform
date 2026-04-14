import logging
from celery import shared_task

logger = logging.getLogger(__name__)

KYC_STATUS_MESSAGES = {
    "pending": ("KYC Submitted", "Your KYC application has been submitted and is awaiting review."),
    "processing": ("KYC Processing", "Your KYC application is being processed."),
    "approved": ("KYC Approved! 🎉", "Congratulations! Your KYC verification has been approved."),
    "rejected": ("KYC Rejected", "Your KYC application has been rejected. Please review and resubmit."),
    "resubmit_required": ("KYC Resubmission Required", "Additional documents are required for your KYC verification."),
}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_kyc_status_notification(self, user_id, kyc_status):
    """Send KYC status notifications via all channels."""
    from django.contrib.auth import get_user_model
    from apps.notifications.services import NotificationService

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for notification.")
        return

    subject, message = KYC_STATUS_MESSAGES.get(
        kyc_status,
        ("KYC Status Update", f"Your KYC status has changed to: {kyc_status}")
    )

    try:
        # Email notification
        NotificationService.send_email(
            to_email=user.email,
            to_name=user.full_name,
            subject=subject,
            message=message,
        )

        # SMS notification
        if user.phone_number and user.is_phone_verified:
            NotificationService.send_sms(user, f"{subject}: {message}")

        # WhatsApp notification
        if user.phone_number and user.is_phone_verified:
            NotificationService.send_whatsapp(user, f"{subject}: {message}")

        logger.info(f"KYC status notifications sent to {user.email} for status: {kyc_status}")

    except Exception as exc:
        logger.error(f"Notification task failed for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_bulk_reminder(self, user_ids, subject, message):
    """Send bulk reminder notifications to a list of users."""
    from django.contrib.auth import get_user_model
    from apps.notifications.services import NotificationService

    User = get_user_model()
    users = User.objects.filter(id__in=user_ids)

    success_count = 0
    for user in users:
        try:
            NotificationService.send_email(
                to_email=user.email,
                to_name=user.full_name,
                subject=subject,
                message=message,
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send reminder to {user.email}: {e}")

    logger.info(f"Bulk reminder sent to {success_count}/{len(user_ids)} users.")
    return {"sent": success_count, "total": len(user_ids)}
