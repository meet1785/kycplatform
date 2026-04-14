from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Custom user model with phone number and KYC-related fields."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class OTPVerification(models.Model):
    """OTP verification model for phone and email verification."""

    OTP_TYPE_CHOICES = [
        ("phone", "Phone"),
        ("email", "Email"),
        ("login", "Login"),
        ("password_reset", "Password Reset"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.otp_type} - {self.code}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
