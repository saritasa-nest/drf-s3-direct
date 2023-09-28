import abc


class HasFieldPermissionMixin:
    """Mixin for checking field permissions."""

    @abc.abstractmethod
    def has_field_permission(self, request, view, obj, field) -> bool:
        """Check if user had permissions for obj's field."""
