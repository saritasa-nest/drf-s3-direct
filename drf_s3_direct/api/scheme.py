from drf_spectacular import utils

from . import serializers, views

utils.extend_schema_view(
    get_params=utils.extend_schema(
        request=serializers.S3RequestParamsSerializer,
        responses=serializers.S3UploadSerializer,
    ),
    get_file=utils.extend_schema(
        request=None,
        responses={
            200: serializers.S3DownloadSerializer,
        },
    ),
    check_file_access=utils.extend_schema(
        request=None,
        responses={
            200: None,
        },
    ),
)(views.S3FileView)
