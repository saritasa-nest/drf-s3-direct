from django.apps import AppConfig


class S3DRFApp(AppConfig):
    """Default configuration for S3DRFApp."""

    name = "drf_s3_direct"
    verbose_name = "DRF-S3-Direct"

    def ready(self) -> None:
        """Prepare app.

        Apply drf-spectacular spec customization.

        """
        try:
            from .api import scheme  # noqa
        except ImportError:
            pass
