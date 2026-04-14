from rest_framework.permissions import BasePermission, IsAdminUser as DRFIsAdminUser


class IsAdminUser(DRFIsAdminUser):
    """Permission class that allows access only to staff/admin users."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """Permission class that allows access to object owner or admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return getattr(obj, "user", None) == request.user or obj == request.user
