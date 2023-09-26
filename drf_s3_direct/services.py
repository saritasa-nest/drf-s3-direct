import dataclasses
import typing

import boto3
import botocore.credentials
from django.conf import settings
from django.contrib.auth import models as auth_models

from . import keys, s3_configs


@dataclasses.dataclass
class AWSCredentials:
    """Representation of aws credentials."""

    token: str | None
    access_key: str | None
    secret_access_key: str | None


@dataclasses.dataclass
class S3UploadParams:
    """Representation of s3 upload params."""

    url: str
    params: dict[str, str]


def get_access_keys() -> tuple[str, str]:
    """Get AWS access keys."""
    access_key = getattr(settings, "AWS_S3_ACCESS_KEY_ID", "")
    if not access_key:
        access_key = getattr(settings, "AWS_ACCESS_KEY_ID", "")

    secret_access_key = getattr(settings, "AWS_S3_SECRET_ACCESS_KEY", "")
    if not secret_access_key:
        secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", "")

    return access_key, secret_access_key


def get_aws_credentials() -> AWSCredentials:
    """Shortcut to get AWS credentials.

    Try to get AWS credentials from settings or from instance profile (if we
    are running on EC2).

    Return:
        AWSCredentials(namedtuple): namedtuple which contains
            * access_key (string) - AWS access key id
            * secret_access_key (string) - AWS secret access key
            * token (string) - AWS session token

    """
    access_key, secret_access_key = get_access_keys()
    token = None
    if access_key is not None and secret_access_key is not None:
        return AWSCredentials(
            access_key=access_key,
            secret_access_key=secret_access_key,
            token=token,
        )
    provider = botocore.credentials.InstanceMetadataProvider(
        iam_role_fetcher=botocore.credentials.InstanceMetadataFetcher(
            timeout=1000,
            num_attempts=2,
        ),
    )
    credentials = provider.load()
    if not credentials:
        return AWSCredentials(
            access_key=None,
            secret_access_key=None,
            token=None,
        )
    return AWSCredentials(
        access_key=credentials.access_key,
        secret_access_key=credentials.secret_key,
        token=credentials.token,
    )


def get_aws_endpoint(region: str | None) -> str:
    """Get aws bucket endpoint."""
    minio_url = get_minio_url()

    if minio_url:
        return minio_url
    if not region or region == "us-east-1":
        return "s3.amazonaws.com"
    return f"s3-{region}.amazonaws.com"


def get_minio_url() -> str:
    """Get minio url."""
    return getattr(settings, "AWS_S3_ENDPOINT_URL", "")


def get_s3_client() -> typing.Any:
    """Prepare s3 client for usage."""
    region = getattr(settings, "AWS_S3_DIRECT_REGION", None)
    endpoint_url = get_aws_endpoint(region=region)
    credentials = get_aws_credentials()
    return boto3.client(
        service_name="s3",
        region_name=region,
        aws_session_token=credentials.token,
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_access_key,
        endpoint_url=endpoint_url,
    )


def get_fields(
    config: s3_configs.S3SupportedFieldConfig,
    content_type: str,
    meta_data: dict[str, str],
) -> dict[str, int | str]:
    """Prepare fields for s3 upload."""
    fields: dict[str, int | str] = {
        "success_action_status": config.success_action_status,
        "acl": config.acl.value,
        "Content-Type": content_type,
    }
    fields.update(**meta_data)
    if config.content_disposition:
        fields["Content-Disposition"] = config.content_disposition
    return fields


def get_conditions(
    config: s3_configs.S3SupportedFieldConfig,
    content_type: str,
    meta_data: dict[str, str],
) -> list[list[str | int] | dict[str, str | int]]:
    """Prepare conditions for s3 upload."""
    conditions: list[list[str | int] | dict[str, str | int]] = [
        {"acl": config.acl.value},
        {"success_action_status": str(config.success_action_status)},
        {"Content-Type": content_type},
    ]
    if config.content_length_range:
        conditions.append(
            ["content-length-range"] + list(config.content_length_range),
        )
    if config.content_disposition:
        conditions.append(
            {"Content-Disposition": config.content_disposition},
        )
    for key, value in meta_data.items():
        conditions.append({key: value})
    return conditions


def generate_params(
    user: auth_models.AbstractBaseUser | auth_models.AnonymousUser | None,
    filename: str,
    config: s3_configs.S3SupportedFieldConfig,
    content_type: str,
    **kwargs,
) -> S3UploadParams:
    """Generate params for s3 upload."""
    s3_client = get_s3_client()
    meta_data = {
        "x-amz-meta-user-id": str(getattr(user, "pk", "anon") or "anon"),
        "x-amz-meta-config-name": config.name,
    }
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_post.html
    s3_params: dict[str, typing.Any] = s3_client.generate_presigned_post(
        settings.AWS_STORAGE_BUCKET_NAME,
        config.key(filename=filename),
        Fields=get_fields(
            config=config,
            content_type=content_type,
            meta_data=meta_data,
        ),
        Conditions=get_conditions(
            config=config,
            content_type=content_type,
            meta_data=meta_data,
        ),
        ExpiresIn=config.expires_in,
    )
    return S3UploadParams(
        url=s3_params["url"],
        params=s3_params["fields"],
    )


def get_download_link(original_url: str) -> str:
    """Generate download link for file."""
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    copy_source = {
        "Bucket": bucket,
        "Key": original_url,
    }
    filename = original_url.split("/")[-1]
    key = keys.S3KeyWithPrefix("downloads")(filename=filename)
    s3_client = get_s3_client()
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/head_object.html
    original_object_meta = s3_client.head_object(
        Bucket=bucket,
        Key=original_url,
    )
    metadata = original_object_meta["Metadata"]
    metadata["original-key"] = original_url
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/copy_object.html
    s3_client.copy_object(
        ACL=s3_configs.ACL.public_read.value,
        Bucket=bucket,
        CopySource=copy_source,
        Key=key,
        ContentDisposition="attachment",
        ContentType=original_object_meta["ContentType"],
        MetadataDirective="REPLACE",
        Metadata=metadata,
    )
    return f"{s3_client._endpoint.host}/{bucket}/{key}"
