import logging
import requests
from django.utils import timezone
from django.conf import settings
from apps.kyc.models import KYCApplication, KYCLog

logger = logging.getLogger(__name__)


def create_kyc_application(user):
    """Create a new KYC application for a user if one doesn't exist."""
    application, created = KYCApplication.objects.get_or_create(user=user)
    return application, created


def submit_kyc_application(application):
    """Submit the KYC application for processing."""
    if application.status not in [KYCApplication.STATUS_PENDING, KYCApplication.STATUS_RESUBMIT]:
        raise ValueError("Application is not in a submittable state.")

    previous_status = application.status
    application.status = KYCApplication.STATUS_PROCESSING
    application.submitted_at = timezone.now()
    application.save(update_fields=["status", "submitted_at"])

    KYCLog.objects.create(
        kyc_application=application,
        action="submitted",
        previous_status=previous_status,
        new_status=KYCApplication.STATUS_PROCESSING,
        details={"submitted_at": application.submitted_at.isoformat()},
    )

    return application


def process_kyc_with_provider(application):
    """
    Call mock or real KYC provider API.
    Returns (success, provider_ref, status, score).
    """
    try:
        # Mock KYC provider integration
        # In production, replace with real KYC API call
        documents = application.documents.all()
        if not documents.exists():
            return False, None, "failed", 0.0

        # Simulate API call to KYC provider
        mock_response = _call_mock_kyc_api(application)
        return (
            mock_response["success"],
            mock_response.get("reference"),
            mock_response.get("status", "pending"),
            mock_response.get("score", 0.0),
        )
    except Exception as e:
        logger.error(f"KYC provider error for application {application.id}: {e}")
        return False, None, "error", 0.0


def _call_mock_kyc_api(application):
    """Mock KYC API response for development/testing."""
    import random

    # Simulate processing time and scoring
    score = round(random.uniform(0.6, 0.99), 2)

    if score >= 0.8:
        return {
            "success": True,
            "reference": f"MOCK-KYC-{application.id}",
            "status": "approved",
            "score": score,
        }
    elif score >= 0.6:
        return {
            "success": True,
            "reference": f"MOCK-KYC-{application.id}",
            "status": "review_required",
            "score": score,
        }
    else:
        return {
            "success": False,
            "reference": f"MOCK-KYC-{application.id}",
            "status": "rejected",
            "score": score,
        }


def update_kyc_status(application, new_status, performed_by=None, reason="", notes=""):
    """Update KYC application status and create a log entry."""
    previous_status = application.status
    application.status = new_status

    if new_status in [KYCApplication.STATUS_APPROVED, KYCApplication.STATUS_REJECTED]:
        application.reviewed_at = timezone.now()
        application.reviewed_by = performed_by

    if reason:
        application.rejection_reason = reason
    if notes:
        application.admin_notes = notes

    application.save()

    KYCLog.objects.create(
        kyc_application=application,
        action=f"status_changed_to_{new_status}",
        previous_status=previous_status,
        new_status=new_status,
        performed_by=performed_by,
        details={"reason": reason, "notes": notes},
    )

    return application


def get_document_signed_url(document):
    """Generate a signed URL for secure document access."""
    if not getattr(settings, "USE_SPACES", False):
        # Local storage - just return the URL
        return document.file.url if document.file else None

    try:
        import boto3
        from botocore.exceptions import ClientError

        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": document.file.name},
            ExpiresIn=3600,  # 1 hour
        )
        return signed_url
    except Exception as e:
        logger.error(f"Error generating signed URL for document {document.id}: {e}")
        return None
