import random
import string
import logging
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_otp(length=None):
    """Generate a numeric OTP code."""
    length = length or getattr(settings, "OTP_LENGTH", 6)
    return "".join(random.choices(string.digits, k=length))


def create_otp(user, otp_type):
    """Create and store an OTP for a user."""
    from apps.authentication.models import OTPVerification

    expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 10)
    code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

    # Invalidate existing OTPs of the same type
    OTPVerification.objects.filter(user=user, otp_type=otp_type, is_verified=False).delete()

    otp = OTPVerification.objects.create(
        user=user,
        otp_type=otp_type,
        code=code,
        expires_at=expires_at,
    )
    return otp


def verify_otp(user, code, otp_type):
    """Verify an OTP code. Returns (success, message)."""
    from apps.authentication.models import OTPVerification

    try:
        otp = OTPVerification.objects.get(
            user=user,
            code=code,
            otp_type=otp_type,
            is_verified=False,
        )
    except OTPVerification.DoesNotExist:
        return False, "Invalid OTP code."

    if otp.is_expired():
        return False, "OTP has expired. Please request a new one."

    otp.is_verified = True
    otp.save(update_fields=["is_verified"])

    # Mark the corresponding field as verified
    if otp_type == "phone":
        user.is_phone_verified = True
        user.save(update_fields=["is_phone_verified"])
    elif otp_type == "email":
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

    return True, "OTP verified successfully."


def send_sms_otp(phone_number, otp_code):
    """Send OTP via Twilio SMS."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your KYC Platform verification code is: {otp_code}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
        logger.info(f"SMS OTP sent to {phone_number}, SID: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS OTP to {phone_number}: {e}")
        return False
