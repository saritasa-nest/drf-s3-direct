import dataclasses
import enum
import typing

from . import keys

S3_CONFIGS: dict[str, "S3SupportedFieldConfig"] = {}


class S3SupportedFieldConfigMeta(type):
    """Meta class for S3SupportedFieldConfig."""

    def __call__(cls, *args, **kwargs) -> "S3SupportedFieldConfig":
        """Update mapping of S3SupportedFieldConfigs."""
        instance: S3SupportedFieldConfig = super().__call__(*args, **kwargs)
        if instance.name in S3_CONFIGS:
            raise ValueError(f"{instance.name} config is already defined")
        S3_CONFIGS[instance.name] = instance
        return instance


class ACL(enum.Enum):
    """Types of ACL.

    https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html

    """

    private = "private"
    public_read = "public-read"
    public_read_write = "public_read_write"
    aws_exec_read = "aws-exec-read"
    authenticated_read = "authenticated_read"
    bucket_owner_read = "bucket-owner-read"
    bucket_owner_full_control = "bucket-owner-full-control"
    log_delivery_write = "log-delivery-write"


@dataclasses.dataclass
class S3SupportedFieldConfig(metaclass=S3SupportedFieldConfigMeta):
    """Configuration for S3 supported field."""

    name: str
    # S3Key are used to generate file's path
    key: keys.S3Key
    # Mime types are allowed, None - for all
    allowed: tuple[str, ...] | None = None
    # Preform checks against user
    auth: typing.Callable[[typing.Any | None], bool] | None = None
    # Define allowed size limits for file (in bytes)
    content_length_range: tuple[int, int] | None = None
    acl: ACL = ACL.public_read
    # In how much second pre-signed URL for upload will expire
    expires_in: int = 3600
    success_action_status: int = 201
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition
    content_disposition: (
        typing.Literal["attachment"] | typing.Literal["inline"]
    ) = "attachment"
