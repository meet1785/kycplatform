from django.urls import path
from apps.kyc.views import (
    KYCApplicationView,
    KYCSubmitView,
    DocumentUploadView,
    DocumentDetailView,
    AdminKYCListView,
    AdminKYCReviewView,
    AdminKYCTriggerView,
    AdminKYCLogsView,
)

urlpatterns = [
    # User KYC endpoints
    path("application/", KYCApplicationView.as_view(), name="kyc-application"),
    path("application/submit/", KYCSubmitView.as_view(), name="kyc-submit"),
    path("documents/", DocumentUploadView.as_view(), name="kyc-documents"),
    path("documents/<uuid:document_id>/", DocumentDetailView.as_view(), name="kyc-document-detail"),
    # Admin endpoints
    path("admin/applications/", AdminKYCListView.as_view(), name="admin-kyc-list"),
    path("admin/applications/<uuid:application_id>/review/", AdminKYCReviewView.as_view(), name="admin-kyc-review"),
    path("admin/applications/<uuid:application_id>/trigger/", AdminKYCTriggerView.as_view(), name="admin-kyc-trigger"),
    path("admin/applications/<uuid:application_id>/logs/", AdminKYCLogsView.as_view(), name="admin-kyc-logs"),
]
