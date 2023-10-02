import os
import time
import xml.etree.ElementTree as ET

import pytest
import requests
from django.conf import settings
from rest_framework import status, test
from rest_framework.response import Response

import drf_s3_direct.services

from . import utils
from .example_app import models


@pytest.mark.parametrize(
    argnames="user",
    argvalues=[
        "anon",
        "user_with_access_to_files",
        "user_with_access_to_special_file",
        "user_with_no_access",
    ],
    indirect=True,
)
def test_file_upload(
    api_client: test.APIClient,
    user: models.User,
) -> None:
    """Test that we can upload file with retrieved params."""
    api_client.force_authenticate(user=user)
    s3_config = "anon_files"
    response: Response = api_client.post(
        path=utils.get_s3_params_url(),
        data={
            "config": s3_config,
            "filename": "test.py",
            "content_type": "text/plain",
            "content_length": os.path.getsize(__file__),
        },
    )  # type: ignore
    assert response.status_code == status.HTTP_200_OK, response.data
    url = response.data["url"]  # type: ignore
    params = response.data["params"]  # type: ignore

    # Test file upload itself
    upload_response: requests.Response = requests.post(
        url=url,
        data=params,
        files={"file": open(__file__, "r")},
    )

    # Validate that request was okay, and we got file url
    assert upload_response.ok, upload_response.content
    file_url = ET.fromstring(upload_response.content.decode())[3].text
    assert file_url, upload_response.content
    file_url = file_url.replace(
        f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}",
        "",
    )
    # Validate metadata
    s3_client = drf_s3_direct.services.get_s3_client()
    original_object_meta = s3_client.head_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_url,
    )
    metadata = original_object_meta["Metadata"]
    assert metadata["config-name"] == s3_config, metadata
    assert metadata["user-id"] == str(getattr(user, "pk", "anon")), metadata


@pytest.mark.parametrize(
    argnames="user",
    argvalues=[
        "anon",
        "user_with_access_to_files",
        "user_with_access_to_special_file",
        "user_with_no_access",
    ],
    indirect=True,
)
def test_file_upload_expired(
    api_client: test.APIClient,
    user: models.User,
) -> None:
    """Test that expiration setting works correctly."""
    api_client.force_authenticate(user=user)
    response: Response = api_client.post(
        path=utils.get_s3_params_url(),
        data={
            "config": "quick_expire_file",
            "filename": "test.txt",
            "content_type": "text/plain",
            "content_length": os.path.getsize(__file__),
        },
    )  # type: ignore
    assert response.status_code == status.HTTP_200_OK, response.data
    url = response.data["url"]  # type: ignore
    params = response.data["params"]  # type: ignore
    # Wait for params to expire
    time.sleep(1)
    upload_response: requests.Response = requests.post(
        url=url,
        data=params,
        files={"file": open(__file__, "r")},
    )
    # Validate that request failed, and we got correct error message
    assert not upload_response.ok, upload_response.content
    error_msg = ET.fromstring(upload_response.content.decode())[1].text
    assert (
        error_msg
        == "Access Denied. (Invalid according to Policy: Policy expired)"
    ), upload_response.content
