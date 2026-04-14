import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }


@pytest.fixture
def user(user_data):
    u = User.objects.create_user(
        email=user_data["email"],
        username=user_data["username"],
        password=user_data["password"],
    )
    return u


class TestRegistration:
    def test_register_success(self, api_client, user_data):
        response = api_client.post("/api/v1/auth/register/", user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert "user" in response.data

    def test_register_password_mismatch(self, api_client, user_data):
        user_data["password_confirm"] = "different"
        response = api_client.post("/api/v1/auth/register/", user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user_data, user):
        response = api_client.post("/api/v1/auth/register/", user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestLogin:
    def test_login_success(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "SecurePass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProfile:
    def test_get_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email
