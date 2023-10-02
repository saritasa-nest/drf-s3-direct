import pytest
import requests
from rest_framework import status, test
from rest_framework.response import Response

from . import utils
from .example_app import models


@pytest.mark.parametrize(
    argnames="user",
    argvalues=[
        "user_with_access_to_files",
        "user_with_access_to_special_file",
        "user_with_no_access",
    ],
    indirect=True,
)
def test_get_download_link_general_permission(
    api_client: test.APIClient,
    user: models.User,
    model_with_files: models.ModelWithFiles,
) -> None:
    """Test that download endpoint works correctly with general permission."""
    api_client.force_authenticate(user=user)
    response: Response = api_client.get(
        path=utils.get_download_url(
            app=model_with_files._meta.app_label,
            model=model_with_files._meta.model_name,  # type: ignore
            pk=model_with_files.pk,
            field="file",
        ),
    )  # type: ignore
    if getattr(user, "has_access_to_files", False) is False:
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.data
        return
    assert response.status_code == status.HTTP_200_OK, response.data
    file_response = requests.get(response.data["url"])  # type: ignore
    assert file_response.ok, file_response.content


@pytest.mark.parametrize(
    argnames="user",
    argvalues=[
        "user_with_access_to_files",
        "user_with_access_to_special_file",
        "user_with_no_access",
    ],
    indirect=True,
)
def test_get_download_link_field_permission(
    api_client: test.APIClient,
    user: models.User,
    model_with_files: models.ModelWithFiles,
) -> None:
    """Test that download endpoint works correctly with special permission."""
    api_client.force_authenticate(user=user)
    response: Response = api_client.get(
        path=utils.get_download_url(
            app=model_with_files._meta.app_label,
            model=model_with_files._meta.model_name,  # type: ignore
            pk=model_with_files.pk,
            field="image",
        ),
    )  # type: ignore
    if getattr(user, "has_access_to_special_file", False) is False:
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.data
        return
    assert response.status_code == status.HTTP_200_OK, response.data
    file_response = requests.get(response.data["url"])  # type: ignore
    assert file_response.ok, file_response.content
