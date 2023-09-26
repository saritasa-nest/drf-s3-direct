import dataclasses
import importlib

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import decorators, response, status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .. import services
from . import permissions, serializers


class S3FileView(viewsets.GenericViewSet):
    """View for getting params for s3."""

    file_path_regex = (
        r"(?P<app>\w+)/(?P<model>\w+)/(?P<pk>[\w-]+)/(?P<field>\w+)"
    )

    serializer_class = serializers.S3RequestParamsSerializer

    @decorators.action(
        methods=["POST"],
        url_path="get-params",
        url_name="get-params",
        detail=False,
    )
    def get_params(self, request: Request) -> response.Response:
        """Get parameters for upload to S3 bucket.

        Current endpoint returns all required for s3 upload data,
        which should be later sent to `url` as `form-data` url with
        'file'. Workflow: First, you make request to this endpoint. Then send
        response data to `url` via `POST`.

        """
        serializer = serializers.S3RequestParamsSerializer(
            context_request=request,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        params = services.generate_params(
            user=request.user,
            **serializer.data,
        )
        return response.Response(
            status=status.HTTP_200_OK,
            data=serializers.S3UploadSerializer(
                instance=dataclasses.asdict(params),
            ).data,
        )

    @decorators.action(
        url_path=f"check-file-access/{file_path_regex}",
        detail=False,
    )
    def check_file_access(
        self,
        request: Request,
        app: str,
        model: str,
        pk: str,
        field: str,
    ) -> response.Response:
        """Check if user has access to file."""
        instance = self.get_instance(
            app=app,
            model=model,
            pk=pk,
        )
        if not self.check_access_permissions(
            instance=instance,
            field=field,
        ):
            raise Http404
        file_field: models.FieldFile | None = getattr(instance, field, None)
        if not file_field:
            raise Http404
        return response.Response(status=status.HTTP_200_OK)

    @decorators.action(
        url_path=f"get-file/{file_path_regex}",
        detail=False,
    )
    def get_file(
        self,
        request: Request,
        app: str,
        model: str,
        pk: str,
        field: str,
    ) -> response.Response:
        """Get download link."""
        instance = self.get_instance(
            app=app,
            model=model,
            pk=pk,
        )
        if not self.check_access_permissions(
            instance=instance,
            field=field,
        ):
            raise Http404
        file_field: models.FieldFile | None = getattr(instance, field, None)
        if not file_field:
            raise Http404
        return response.Response(
            status=status.HTTP_200_OK,
            data=serializers.S3DownloadSerializer(
                instance={
                    "url": services.get_download_link(
                        original_url=file_field.name,
                    ),
                },
            ).data,
        )

    def get_instance(
        self,
        app: str,
        model: str,
        pk: str,
    ) -> models.Model:
        """Get instance via app, model and pk params."""
        model_class = get_object_or_404(
            klass=ContentType,
            app_label=app,
            model=model,
        ).model_class()
        if not model_class:
            raise Http404
        return get_object_or_404(
            klass=model_class,
            pk=pk,
        )

    def check_access_permissions(
        self,
        instance: models.Model,
        field: str,
    ) -> bool:
        """Check if user can access to file."""
        permission_path = settings.S3_FILE_PERMISSION_MAPPING.get(
            f"{instance._meta.app_label}.{instance._meta.model_name}",
            settings.DEFAULT_S3_FILE_PERMISSION,
        )
        if not permission_path:
            raise ImproperlyConfigured(
                "No permissions for files set, "
                "please set up S3_FILE_PERMISSION_MAPPING or "
                "DEFAULT_S3_FILE_PERMISSION in settings.",
            )
        *permission_module, permission_name = permission_path.split(".")
        permission: BasePermission = getattr(
            importlib.import_module(".".join(permission_module)),
            permission_name,
        )()
        if isinstance(permission, permissions.HasFieldPermissionMixin):
            return permission.has_field_permission(
                request=self.request,
                view=self,
                obj=instance,
                field=field,
            )
        return permission.has_object_permission(
            request=self.request,
            view=self,
            obj=instance,
        )
