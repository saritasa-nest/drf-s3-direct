from django.db.models import Field, FileField, ImageField
from rest_framework import serializers

import drf_s3_direct.api.fields

from .. import models


class ModelWithFilesSerializer(serializers.ModelSerializer):
    """Serializer to show info model with files."""

    class Meta:
        model = models.ModelWithFiles
        fields = "__all__"

    @property
    def serializer_field_mapping(
        self,
    ) -> dict[Field, serializers.Field]:
        """Extend serializer mapping with custom fields."""
        serializer_field_mapping = super().serializer_field_mapping
        serializer_field_mapping[
            FileField
        ] = drf_s3_direct.api.fields.S3FileField
        serializer_field_mapping[
            ImageField
        ] = drf_s3_direct.api.fields.S3FileField
        return serializer_field_mapping  # type: ignore
