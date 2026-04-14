from rest_framework import serializers
from apps.kyc.models import KYCApplication, KYCDocument, KYCLog


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ["id", "document_type", "file", "file_name", "file_size", "mime_type", "is_verified", "created_at"]
        read_only_fields = ["id", "file_name", "file_size", "mime_type", "is_verified", "created_at"]

    def create(self, validated_data):
        file = validated_data.get("file")
        if file:
            validated_data["file_name"] = file.name
            validated_data["file_size"] = file.size
            validated_data["mime_type"] = getattr(file, "content_type", "")
        return super().create(validated_data)


class KYCLogSerializer(serializers.ModelSerializer):
    performed_by_email = serializers.CharField(source="performed_by.email", read_only=True, allow_null=True)

    class Meta:
        model = KYCLog
        fields = ["id", "action", "previous_status", "new_status", "performed_by_email", "details", "created_at"]
        read_only_fields = fields


class KYCApplicationSerializer(serializers.ModelSerializer):
    documents = KYCDocumentSerializer(many=True, read_only=True)
    logs = KYCLogSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = KYCApplication
        fields = [
            "id", "user_email", "user_full_name", "status",
            "date_of_birth", "nationality",
            "address_line1", "address_line2", "city", "state", "postal_code", "country",
            "kyc_provider_ref", "kyc_provider_status", "kyc_score",
            "rejection_reason", "admin_notes",
            "submitted_at", "reviewed_at", "created_at", "updated_at",
            "documents", "logs",
        ]
        read_only_fields = [
            "id", "user_email", "user_full_name", "status",
            "kyc_provider_ref", "kyc_provider_status", "kyc_score",
            "submitted_at", "reviewed_at", "created_at", "updated_at",
            "documents", "logs",
        ]


class KYCApplicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for users to update their KYC application details."""

    class Meta:
        model = KYCApplication
        fields = [
            "date_of_birth", "nationality",
            "address_line1", "address_line2", "city", "state", "postal_code", "country",
        ]


class AdminKYCReviewSerializer(serializers.Serializer):
    """Serializer for admin to approve/reject KYC applications."""
    action = serializers.ChoiceField(choices=["approve", "reject", "request_resubmit"])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    admin_notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["action"] in ["reject", "request_resubmit"] and not attrs.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required."})
        return attrs
