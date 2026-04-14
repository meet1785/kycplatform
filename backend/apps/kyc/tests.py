import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.kyc.models import KYCApplication

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="kyc@example.com",
        username="kycuser",
        password="SecurePass123!",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


class TestKYCApplication:
    def test_get_or_create_application(self, authenticated_client):
        response = authenticated_client.get("/api/v1/kyc/application/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "pending"

    def test_update_application(self, authenticated_client):
        data = {
            "date_of_birth": "1990-01-01",
            "nationality": "US",
            "address_line1": "123 Main St",
            "city": "New York",
            "country": "US",
        }
        response = authenticated_client.put("/api/v1/kyc/application/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "New York"

    def test_submit_without_documents(self, authenticated_client):
        response = authenticated_client.post("/api/v1/kyc/application/submit/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
