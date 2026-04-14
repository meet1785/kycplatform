import uuid
import hashlib


def generate_unique_filename(filename):
    """Generate a unique filename while preserving the extension."""
    ext = filename.split(".")[-1] if "." in filename else ""
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}" if ext else unique_name


def mask_sensitive_data(data, fields=None):
    """Mask sensitive fields in a dictionary."""
    if fields is None:
        fields = ["password", "token", "secret", "key", "otp"]
    masked = {}
    for key, value in data.items():
        if any(field in key.lower() for field in fields):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked
