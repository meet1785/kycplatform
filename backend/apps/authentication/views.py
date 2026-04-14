from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from apps.authentication.serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)
from apps.authentication.services import create_otp, verify_otp, send_sms_otp

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login with email and password."""
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """Logout and blacklist refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Authentication"])
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update current user profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Authentication"])
    def get_object(self):
        return self.request.user


class RequestOTPView(APIView):
    """Request an OTP for phone or email verification."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Authentication"])
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        otp_type = serializer.validated_data["otp_type"]
        phone_number = serializer.validated_data.get("phone_number")

        if phone_number:
            user.phone_number = phone_number
            user.save(update_fields=["phone_number"])

        otp = create_otp(user, otp_type)

        if otp_type in ["phone", "login"] and user.phone_number:
            send_sms_otp(user.phone_number, otp.code)

        return Response(
            {"detail": f"OTP sent successfully. Valid for 10 minutes."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    """Verify an OTP code."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Authentication"])
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data["code"]
        otp_type = serializer.validated_data["otp_type"]

        success, message = verify_otp(user, code, otp_type)
        if not success:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": message}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Change user password."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Authentication"])
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
