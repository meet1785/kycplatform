from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.authentication.models import User, OTPVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "username", "first_name", "last_name", "is_phone_verified", "is_active", "created_at"]
    list_filter = ["is_phone_verified", "is_email_verified", "is_active", "is_staff"]
    search_fields = ["email", "username", "first_name", "last_name", "phone_number"]
    ordering = ["-created_at"]
    fieldsets = UserAdmin.fieldsets + (
        ("KYC Platform", {"fields": ("phone_number", "is_phone_verified", "is_email_verified", "avatar")}),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ["user", "otp_type", "code", "is_verified", "expires_at", "created_at"]
    list_filter = ["otp_type", "is_verified"]
    search_fields = ["user__email", "code"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
