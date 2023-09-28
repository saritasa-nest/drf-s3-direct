import imagekit.models

from . import fields


class S3ProcessedImageField(
    fields.S3FileFieldMixin,
    imagekit.models.ProcessedImageField,
):
    """Add s3 support for imagekit's ProcessedImageField."""
