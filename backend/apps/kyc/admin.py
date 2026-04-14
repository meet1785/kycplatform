from django.contrib import admin
from apps.kyc.models import KYCApplication, KYCDocument, KYCLog


class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 0
    readonly_fields = ["file_name", "file_size", "mime_type", "is_verified", "created_at"]


class KYCLogInline(admin.TabularInline):
    model = KYCLog
    extra = 0
    readonly_fields = ["action", "previous_status", "new_status", "performed_by", "details", "created_at"]
    can_delete = False


@admin.register(KYCApplication)
class KYCApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "kyc_score", "submitted_at", "reviewed_at", "reviewed_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "kyc_provider_ref", "kyc_provider_status", "kyc_score", "submitted_at", "reviewed_at", "created_at", "updated_at"]
    inlines = [KYCDocumentInline, KYCLogInline]
    actions = ["approve_applications", "reject_applications", "trigger_verification"]

    def approve_applications(self, request, queryset):
        from apps.kyc.services import update_kyc_status
        from apps.notifications.tasks import send_kyc_status_notification
        for application in queryset:
            update_kyc_status(application, "approved", performed_by=request.user)
            send_kyc_status_notification.delay(str(application.user.id), "approved")
        self.message_user(request, f"Approved {queryset.count()} applications.")
    approve_applications.short_description = "Approve selected KYC applications"

    def reject_applications(self, request, queryset):
        from apps.kyc.services import update_kyc_status
        from apps.notifications.tasks import send_kyc_status_notification
        for application in queryset:
            update_kyc_status(application, "rejected", performed_by=request.user, reason="Rejected by admin.")
            send_kyc_status_notification.delay(str(application.user.id), "rejected")
        self.message_user(request, f"Rejected {queryset.count()} applications.")
    reject_applications.short_description = "Reject selected KYC applications"

    def trigger_verification(self, request, queryset):
        from apps.kyc.tasks import process_kyc_verification
        for application in queryset:
            process_kyc_verification.delay(str(application.id))
        self.message_user(request, f"Verification triggered for {queryset.count()} applications.")
    trigger_verification.short_description = "Trigger KYC verification"


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ["kyc_application", "document_type", "file_name", "file_size", "is_verified", "created_at"]
    list_filter = ["document_type", "is_verified"]
    search_fields = ["kyc_application__user__email", "file_name"]
    readonly_fields = ["file_name", "file_size", "mime_type", "created_at", "updated_at"]


@admin.register(KYCLog)
class KYCLogAdmin(admin.ModelAdmin):
    list_display = ["kyc_application", "action", "previous_status", "new_status", "performed_by", "created_at"]
    list_filter = ["action", "new_status"]
    search_fields = ["kyc_application__user__email"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]
