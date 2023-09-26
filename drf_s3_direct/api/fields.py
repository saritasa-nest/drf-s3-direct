import collections
import collections.abc
import typing
from urllib.parse import unquote, unquote_plus, urlparse

from botocore.exceptions import ParamValidationError
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import MinLengthValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.settings import api_settings

from .. import s3_configs


class S3ConfigField(serializers.ChoiceField):
    """Custom Choice field for s3 configs."""

    def __init__(self, **kwargs) -> None:
        super().__init__(choices=tuple(), **kwargs)

    def _get_choices(self) -> collections.OrderedDict[str, str]:
        """Get choices from s3_configs.S3_CONFIGS."""
        current_choices = tuple(
            (
                config_name,
                config_name,
            )
            for config_name in s3_configs.S3_CONFIGS
        )
        choices = super()._get_choices()
        if current_choices != choices:
            self._set_choices(current_choices)
        return super()._get_choices()

    def _set_choices(self, choices) -> None:
        """Update choices.

        Redefined to avoid recursion.

        """
        self.grouped_choices = fields.to_choices_dict(choices)
        self._choices = fields.flatten_choices_dict(self.grouped_choices)

        # Map the string representation of choices to the underlying value.
        # Allows us to deal with eg. integer choices while supporting either
        # integer or string input, but still get the correct datatype out.
        self.choice_strings_to_values = {
            str(key): key for key in self._choices
        }

    choices = property(_get_choices, _set_choices)

    def to_internal_value(
        self,
        data: typing.Any,
    ) -> s3_configs.S3SupportedFieldConfig | None:
        """Convert api data to S3SupportedFieldConfig."""
        try:
            return s3_configs.S3_CONFIGS[str(data)]
        except KeyError:
            self.fail("invalid_choice", input=data)


class S3UploadURLField(serializers.URLField):
    """Special URL serializer field for S3.

    This field allows to save file from its link without domain.

    """

    def __init__(self, **kwargs) -> None:
        """Make custom initialization.

        Add URLValidator to self, but don't add it to self.validators, because
        now validation is called after `to_internal_value`. So it provides
        validation before `to_internal_value`.

        """
        super(serializers.URLField, self).__init__(**kwargs)
        self.validator = URLValidator(message=self.error_messages["invalid"])

        # Append this validator to enable invalid code for spec
        validator_for_spec = MinLengthValidator(
            0,
            message=self.error_messages["invalid"],
        )
        validator_for_spec.code = "invalid"
        self.validators.append(validator_for_spec)

    def to_internal_value(self, data: typing.Any) -> str:
        """Validate `data` and convert it to internal value.

        Cut domain from url to save it in file field.

        """
        if not isinstance(data, str):
            self.fail("invalid")
        self.validator(value=data)

        # Crop server domain and port and get relative path to avatar
        file_url = urlparse(url=data).path

        if file_url.startswith(settings.MEDIA_URL):
            # In case of local storing crop the media prefix
            file_url = file_url[len(settings.MEDIA_URL) :]
        elif (
            getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
            and settings.AWS_STORAGE_BUCKET_NAME in file_url
        ):
            # In case of S3 upload crop S3 bucket name
            file_url = file_url.split(
                f"{settings.AWS_STORAGE_BUCKET_NAME}/",
            )[-1]

        # Normalize URL
        is_minio = getattr(settings, "AWS_IS_MINIO", False)
        if is_minio:
            file_url = unquote(unquote(file_url))
        else:
            file_url = unquote_plus(file_url)

        # If url comes not from s3, then botocore on url validation will
        # raise ParamValidationError
        try:
            if not default_storage.exists(file_url):
                raise serializers.ValidationError(
                    _("File does not exist."),
                )
        except ParamValidationError as error:
            raise serializers.ValidationError(error) from error

        return file_url

    def to_representation(self, value) -> str | None:
        """Return full file url."""
        if not value:
            return None

        use_url = getattr(
            self,
            "use_url",
            api_settings.UPLOADED_FILES_USE_URL,
        )

        if use_url:
            if not getattr(value, "url", None):
                # If the file has not been saved it may not have a URL.
                return None
            url = value.url
            request = self.context.get("request", None)
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return value.name


class DownloadURLParamsField(serializers.Serializer):
    """Params for generating download link."""

    app = serializers.CharField()
    model = serializers.CharField()
    id = serializers.CharField()
    field = serializers.CharField()


class S3FileField(serializers.Serializer):
    """Serializer for representation of s3 file fields."""

    original_url = S3UploadURLField()
    access = serializers.ChoiceField(
        read_only=True,
        choices=tuple((alc.value, alc.value) for alc in s3_configs.ACL),
    )
    download_link_params = DownloadURLParamsField(
        read_only=True,
    )

    def __init__(self, **kwargs) -> None:
        url_max_length = kwargs.pop("max_length", None)
        url_allow_null = kwargs.get("allow_null", False)
        url_required = kwargs.get("required", True)
        super().__init__(**kwargs)
        self.fields["original_url"].max_length = url_max_length
        self.fields["original_url"].allow_null = url_allow_null
        self.fields["original_url"].required = url_required

    def get_attribute(self, instance: models.Model) -> models.Model:
        """Get whole model, instead of attribute."""
        return instance

    def to_representation(
        self,
        value: models.Model,
    ) -> collections.OrderedDict[str, typing.Any]:
        """Convert field to proper data."""
        field_name: str = self.field_name  # type: ignore
        return super().to_representation(
            {
                "access": value._meta.get_field(
                    field_name,
                ).config.acl.value,  # type: ignore
                "original_url": getattr(value, field_name),
                "download_link_params": {
                    "app": value._meta.app_label,
                    "model": value._meta.model_name,
                    "id": value.pk,
                    "field": field_name,
                },
            },
        )

    def validate_empty_values(
        self,
        data: typing.Any,
    ) -> tuple[bool, typing.Any]:
        """Process data for empty values and presence of original_url."""
        is_empty, data = super().validate_empty_values(data)
        if is_empty:
            return is_empty, data
        if "original_url" not in data:  # type: ignore
            return True, None
        return False, data

    def to_internal_value(
        self,
        data: dict[str, typing.Any],
    ) -> str | None:
        """Get link from input data."""
        data = super().to_internal_value(data=data)
        return data.get("original_url")
