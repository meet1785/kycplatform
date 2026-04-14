from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


def kyc_document_upload_path(instance, filename):
    return f"kyc/{instance.kyc_application.user.id}/documents/{filename}"


class KYCApplication(models.Model):
    """KYC Application model representing a user's KYC submission."""

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_RESUBMIT = "resubmit_required"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_RESUBMIT, "Resubmit Required"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kyc_application")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # KYC provider response
    kyc_provider_ref = models.CharField(max_length=255, blank=True)
    kyc_provider_status = models.CharField(max_length=100, blank=True)
    kyc_score = models.FloatField(blank=True, null=True)

    # Admin fields
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_kyc_applications"
    )
    rejection_reason = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    submitted_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kyc_applications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.status}"


class KYCDocument(models.Model):
    """Document uploaded for KYC verification."""

    DOCUMENT_TYPES = [
        ("passport", "Passport"),
        ("national_id", "National ID"),
        ("drivers_license", "Driver's License"),
        ("utility_bill", "Utility Bill"),
        ("bank_statement", "Bank Statement"),
        ("selfie", "Selfie"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_application = models.ForeignKey(KYCApplication, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=kyc_document_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    signed_url = models.TextField(blank=True)
    signed_url_expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kyc_documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kyc_application.user.email} - {self.document_type}"


class KYCLog(models.Model):
    """Audit log for KYC workflow events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kyc_application = models.ForeignKey(KYCApplication, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=100)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="kyc_actions"
    )
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kyc_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kyc_application.user.email} - {self.action}"
