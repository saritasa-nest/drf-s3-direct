import typing

import humanize
from rest_framework import exceptions, request, serializers

from .. import s3_configs
from . import fields


class S3RequestParamsSerializer(serializers.Serializer):
    """Serializer for validation s3 uploading fields."""

    config = fields.S3ConfigField()
    filename = serializers.CharField()
    content_type = serializers.CharField()
    content_length = serializers.IntegerField()

    def __init__(
        self,
        context_request: request.Request | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Set current user."""
        super().__init__(*args, **kwargs)
        self._request: request.Request | None = context_request
        self._user = getattr(self._request, "user", None)

    def validate_config(
        self,
        config: s3_configs.S3SupportedFieldConfig,
    ) -> s3_configs.S3SupportedFieldConfig:
        """Check that user can use dest."""
        if config.auth and not config.auth(self._user):
            raise exceptions.ValidationError(
                "Current user can't use this destination",
            )
        return config

    def validate(self, attrs: dict[str, typing.Any]) -> dict[str, typing.Any]:
        """Preform validations."""
        errors: dict[str, str] = {}
        config: s3_configs.S3SupportedFieldConfig = attrs["config"]
        filename: str = attrs["filename"]
        content_type: str = attrs["content_type"]
        content_length: int = attrs["content_length"]
        if config.allowed and content_type not in config.allowed:
            expected = ", ".join(config.allowed)
            errors["content_type"] = (
                f"Invalid file type - `{content_type}` of `{filename}`. "
                f"Expected: {expected}."
            )
        if config.content_length_range:
            min_bound, max_bound = config.content_length_range
            if min_bound > content_length:
                errors["content_length"] = (
                    "Invalid file size "
                    f"- {humanize.naturalsize(content_length)} "
                    f"of {filename}. "
                    f"Need between {humanize.naturalsize(min_bound)} "
                    f"and {humanize.naturalsize(max_bound)}."
                )
            if max_bound < content_length:
                errors["content_length"] = (
                    "Invalid file size "
                    f"- {humanize.naturalsize(content_length)} "
                    f"of {filename}. "
                    f"Need between {humanize.naturalsize(min_bound)} "
                    f"and {humanize.naturalsize(max_bound)}."
                )
        if errors:
            raise exceptions.ValidationError(errors)
        return attrs


class S3ParamsSerializer(serializers.Serializer):
    """Serializer for showing params for s3 upload."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        fields = (
            "success_action_status",
            "acl",
            "Content-Disposition",
            "x-amz-meta-user-id",
            "x-amz-meta-config-name",
            "Content-Type",
            "key",
            "x-amz-algorithm",
            "x-amz-credential",
            "x-amz-date",
            "policy",
            "x-amz-signature",
        )
        for field in fields:
            self.fields[field] = serializers.CharField(
                label=field,
                required=False,
            )


class S3UploadSerializer(serializers.Serializer):
    """Serializer auto swagger documentation.

    This serializer used just for packages that capable to generate
    openapi/swagger specs, so that front-end team
    could see specs for response for view.

    """

    url = serializers.URLField()
    params = S3ParamsSerializer()


class S3DownloadSerializer(serializers.Serializer):
    """Serializer to represent download link."""

    url = serializers.URLField()
