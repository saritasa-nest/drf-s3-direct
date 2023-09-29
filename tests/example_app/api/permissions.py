from rest_framework import permissions


class CheckPermissionToFile(permissions.BasePermission):
    """Check if user has permissions for files."""

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if user has permissions for files."""
        return request.user.has_access_to_files


class CheckPermissionToSpecialFile(
    permissions.BasePermission,
):
    """Check if user has permissions for special files."""

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if user has permissions for special files."""
        return request.user.has_access_to_special_file
