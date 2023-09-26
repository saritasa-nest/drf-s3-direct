# drf-s3-direct

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/saritasa-nest/drf-s3-direct/checks.yml)
![PyPI](https://img.shields.io/pypi/v/drf-s3-direct)
![PyPI - Status](https://img.shields.io/pypi/status/drf-s3-direct)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drf-s3-direct)
![PyPI - License](https://img.shields.io/pypi/l/drf-s3-direct)
![PyPI - Downloads](https://img.shields.io/pypi/dm/drf-s3-direct)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

Extension for django and drf to ease work with S3

## Installation

```bash
pip install drf-s3-direct
```

or if you are using [poetry](https://python-poetry.org/)

```bash
poetry add drf-s3-direct
```

To install all optional dependencies add `[all]`

## Features

### S3FileField and S3FileFieldMixin

You can use `S3FileField` field to configure where file will be saved,
upload restrictions, permissions and etc. You can use `S3FileField` and
`S3ImageField`. You can extend yours' fields via `S3FileFieldMixin`.

Here an example

```python
from drf_s3_direct.fields import S3ImageField
from drf_s3_direct.keys import S3KeyWithPrefix
from drf_s3_direct.s3_configs import S3SupportedFieldConfig

from django.db.models import Model


class SomeModel(Model):
    image = S3ImageField(
        blank=True,
        null=True,
        config=S3SupportedFieldConfig(
            name="images",
            key=S3KeyWithPrefix("images"),
            allowed=(
                "image/jpeg",
                "image/png",
            ),
            auth=lambda user: user.is_authenticated,
            content_length_range=(5000, 20000000),
        ),
        verbose_name=_("Image"),
    )
```

### API

#### S3FileView

This viewset, which can be used for getting params for file upload,
checking if user has permissions for file, and generating url
for downloading file.

You can add it to your app like this:

```python
path("s3/", include("django_drf_s3.api.urls")),
```

Also you would need to set up `S3_FILE_PERMISSION_MAPPING` or
`DEFAULT_S3_FILE_PERMISSION` in settings.

* `DEFAULT_S3_FILE_PERMISSION` - a path to drf's permission class
* `S3_FILE_PERMISSION_MAPPING` - mapping of `app.model` as key and path to
  drf's permission class

For example:

```python
DEFAULT_S3_FILE_PERMISSION = "rest_framework.permissions.AllowAny"
S3_FILE_PERMISSION_MAPPING = {
    "app.model1": "apps.app.api.permissions.InstancePermission",
    "app.model2": "apps.app.api.permissions.InstancePermissionWithHasFieldPermissionMixin",
}
```

##### get_params

A endpoint which allows you get params for s3 upload based on
supplied configuration.

##### get-file/{app}/{model}/{id}/{field}/

Copies file to download folder in bucket and returns to link of new object.
This folder can be configured in s3 to expire files in 24 hours.

##### check-file-access/{app}/{model}/{id}/{field}/

Endpoint allows to check if user has access to file or not.
Returns `200` or `404`(`403` if you raise Permission error in your permission class).

#### S3FileField

Special field which can be used to show original files path in s3 and params
for getting download link.

```json
{
  "image": {
    "original_url": "path/to/file.png",
    "access": "private",
    "download_link_params": {
      "app": "example",
      "model": "simple_model",
      "id": "12345",
      "field": "image"
    }
  }
}
```

Example:

```python
class ModelObjSerializer(ModelSerializer):

    image = fields.S3FileField()

    class Meta:
        model = models.ModelObj
        fields = (
            "id",
            "image",
        )
```

Or if you need just url

```python
class ModelObjSerializer(ModelSerializer):

    image = fields.S3UploadURLField()

    class Meta:
        model = models.ModelObj
        fields = (
            "id",
            "image",
        )
```
