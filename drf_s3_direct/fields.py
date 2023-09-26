from django.core.files import utils
from django.db import models

from . import s3_configs


class S3FileFieldMixin:
    """Mixin which add support for s3 configuration."""

    def __init__(
        self,
        config: s3_configs.S3SupportedFieldConfig | None = None,
        verbose_name: str | None = None,
        **kwargs,
    ) -> None:
        self.config: s3_configs.S3SupportedFieldConfig | None = config
        super().__init__(
            verbose_name=verbose_name,  # type: ignore
            **kwargs,
        )

    def generate_filename(self, instance: models.Model, filename: str) -> str:
        """Generate filename via config."""
        if self.config is None:
            raise ValueError(
                "Config is set to None, this should not be happening.",
            )
        filename = self.config.key(filename=filename)
        filename = utils.validate_file_name(  # type: ignore
            filename,
            allow_relative_path=True,
        )
        return self.storage.generate_filename(filename)  # type: ignore


class S3FileField(S3FileFieldMixin, models.FileField):
    """FileField with S3 capabilities."""


class S3ImageField(S3FileFieldMixin, models.ImageField):
    """FileField with S3 capabilities."""
