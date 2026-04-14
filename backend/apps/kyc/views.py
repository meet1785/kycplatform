from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from apps.kyc.models import KYCApplication, KYCDocument, KYCLog
from apps.kyc.serializers import (
    KYCApplicationSerializer,
    KYCApplicationUpdateSerializer,
    KYCDocumentSerializer,
    KYCLogSerializer,
    AdminKYCReviewSerializer,
)
from apps.kyc.services import (
    create_kyc_application,
    submit_kyc_application,
    update_kyc_status,
    get_document_signed_url,
)
from apps.core.permissions import IsAdminUser


class KYCApplicationView(APIView):
    """Get or create the current user's KYC application."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["KYC"])
    def get(self, request):
        application, _ = create_kyc_application(request.user)
        serializer = KYCApplicationSerializer(application)
        return Response(serializer.data)

    @extend_schema(tags=["KYC"])
    def put(self, request):
        application, _ = create_kyc_application(request.user)
        serializer = KYCApplicationUpdateSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(KYCApplicationSerializer(application).data)


class KYCSubmitView(APIView):
    """Submit KYC application for processing."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["KYC"])
    def post(self, request):
        from apps.kyc.tasks import process_kyc_verification

        application, _ = create_kyc_application(request.user)

        if not application.documents.exists():
            return Response(
                {"detail": "Please upload at least one document before submitting."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application = submit_kyc_application(application)
        except ValueError:
            return Response(
                {"detail": "Application cannot be submitted in its current state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Trigger background processing
        process_kyc_verification.delay(str(application.id))

        return Response(
            {"detail": "KYC application submitted successfully.", "status": application.status},
            status=status.HTTP_200_OK,
        )


class DocumentUploadView(APIView):
    """Upload documents for KYC verification."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(tags=["KYC"])
    def post(self, request):
        application, _ = create_kyc_application(request.user)

        if application.status not in [KYCApplication.STATUS_PENDING, KYCApplication.STATUS_RESUBMIT]:
            return Response(
                {"detail": "Cannot upload documents in current application state."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = KYCDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save(kyc_application=application)
        return Response(KYCDocumentSerializer(document).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["KYC"])
    def get(self, request):
        application, _ = create_kyc_application(request.user)
        documents = application.documents.all()
        serializer = KYCDocumentSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentDetailView(APIView):
    """Get signed URL for a document."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["KYC"])
    def get(self, request, document_id):
        document = get_object_or_404(
            KYCDocument,
            id=document_id,
            kyc_application__user=request.user,
        )
        signed_url = get_document_signed_url(document)
        return Response({"signed_url": signed_url, "document": KYCDocumentSerializer(document).data})

    @extend_schema(tags=["KYC"])
    def delete(self, request, document_id):
        document = get_object_or_404(
            KYCDocument,
            id=document_id,
            kyc_application__user=request.user,
        )
        application = document.kyc_application
        if application.status not in [KYCApplication.STATUS_PENDING, KYCApplication.STATUS_RESUBMIT]:
            return Response(
                {"detail": "Cannot delete documents in current application state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        document.file.delete(save=False)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Admin Views
class AdminKYCListView(generics.ListAPIView):
    """Admin view to list all KYC applications."""
    serializer_class = KYCApplicationSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["status"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "submitted_at", "reviewed_at"]

    def get_queryset(self):
        return KYCApplication.objects.select_related("user", "reviewed_by").prefetch_related("documents", "logs")


class AdminKYCReviewView(APIView):
    """Admin view to approve/reject KYC applications."""
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["Admin - KYC"])
    def post(self, request, application_id):
        application = get_object_or_404(KYCApplication, id=application_id)
        serializer = AdminKYCReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        reason = serializer.validated_data.get("rejection_reason", "")
        notes = serializer.validated_data.get("admin_notes", "")

        status_map = {
            "approve": KYCApplication.STATUS_APPROVED,
            "reject": KYCApplication.STATUS_REJECTED,
            "request_resubmit": KYCApplication.STATUS_RESUBMIT,
        }

        new_status = status_map[action]
        application = update_kyc_status(
            application,
            new_status,
            performed_by=request.user,
            reason=reason,
            notes=notes,
        )

        # Send notifications
        from apps.notifications.tasks import send_kyc_status_notification
        send_kyc_status_notification.delay(str(application.user.id), new_status)

        # WebSocket notification
        from apps.kyc.tasks import notify_kyc_update
        notify_kyc_update(str(application.user.id), new_status, str(application.id))

        return Response(
            {"detail": f"KYC application {action}d successfully.", "status": new_status},
            status=status.HTTP_200_OK,
        )


class AdminKYCTriggerView(APIView):
    """Admin view to manually trigger KYC verification."""
    permission_classes = [IsAdminUser]

    @extend_schema(tags=["Admin - KYC"])
    def post(self, request, application_id):
        from apps.kyc.tasks import process_kyc_verification

        application = get_object_or_404(KYCApplication, id=application_id)
        process_kyc_verification.delay(str(application.id))
        return Response({"detail": "KYC verification triggered."}, status=status.HTTP_200_OK)


class AdminKYCLogsView(generics.ListAPIView):
    """Admin view to see KYC audit logs."""
    serializer_class = KYCLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        application_id = self.kwargs.get("application_id")
        return KYCLog.objects.filter(kyc_application_id=application_id).select_related("performed_by")
