from django.contrib.auth.models import AbstractUser
from django.db import models

import drf_s3_direct.fields
import drf_s3_direct.keys
import drf_s3_direct.s3_configs


class User(AbstractUser):
    """Custom user model."""

    has_access_to_files = models.BooleanField(default=False)
    has_access_to_special_file = models.BooleanField(default=False)


class ModelWithFiles(models.Model):
    """Test model with different files configs."""

    file = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="files",
            key=drf_s3_direct.keys.S3KeyWithPrefix("files"),
            allowed=("text/plain",),
            auth=lambda user: bool(user and user.is_authenticated),
            content_length_range=(5000, 20000000),
        ),
    )

    private_file = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="private_file",
            key=drf_s3_direct.keys.S3KeyWithPrefix("private_file"),
            allowed=("text/plain",),
            content_length_range=(5000, 20000000),
            acl=drf_s3_direct.s3_configs.ACL.private,
        ),
    )

    quick_expire_file = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="quick_expire_file",
            key=drf_s3_direct.keys.S3KeyWithPrefix("quick_expire_file"),
            expires_in=1,
        ),
    )

    all_file_types = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="all_file_types",
            key=drf_s3_direct.keys.S3KeyWithPrefix("all_file_types"),
            content_length_range=(5000, 20000000),
        ),
    )

    all_file_sizes = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="all_file_sizes",
            key=drf_s3_direct.keys.S3KeyWithPrefix("all_file_sizes"),
        ),
    )

    anon_files = drf_s3_direct.fields.S3FileField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="anon_files",
            key=drf_s3_direct.keys.S3KeyWithPrefix("anon_files"),
        ),
    )

    small_file = drf_s3_direct.fields.S3ImageField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="small_file",
            key=drf_s3_direct.keys.S3KeyWithPrefix("small_file"),
            content_length_range=(0, 1),
        ),
    )

    image = drf_s3_direct.fields.S3ImageField(
        blank=True,
        null=True,
        config=drf_s3_direct.s3_configs.S3SupportedFieldConfig(  # type: ignore
            name="images",
            key=drf_s3_direct.keys.S3KeyWithPrefix("images"),
            allowed=("image/png",),
            content_length_range=(5000, 20000000),
        ),
    )
