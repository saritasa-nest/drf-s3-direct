import pytest
from _pytest.fixtures import SubRequest
from rest_framework import test

from .example_app import factories, models


@pytest.fixture(scope="session", autouse=True)
def django_db_setup(django_db_setup):
    """Set up test db for testing."""


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(django_db_setup, db):
    """Allow all tests to access DB."""


@pytest.fixture
def api_client() -> test.APIClient:
    """Create api client."""
    return test.APIClient()


@pytest.fixture(scope="session")
def user_with_access_to_files(django_db_blocker) -> models.User:
    """Create user with access to files."""
    with django_db_blocker.unblock():
        return factories.UserFactory(
            has_access_to_files=True,
            has_access_to_special_file=False,
        )  # type: ignore


@pytest.fixture(scope="session")
def user_with_access_to_special_file(django_db_blocker) -> models.User:
    """Create user with access to files."""
    with django_db_blocker.unblock():
        return factories.UserFactory(
            has_access_to_files=True,
            has_access_to_special_file=True,
        )  # type: ignore


@pytest.fixture(scope="session")
def user_with_no_access(django_db_blocker) -> models.User:
    """Create user with access to files."""
    with django_db_blocker.unblock():
        return factories.UserFactory(
            has_access_to_files=False,
            has_access_to_special_file=False,
        )  # type: ignore


@pytest.fixture
def user(
    request: SubRequest,
    user_with_access_to_files: models.User,
    user_with_access_to_special_file: models.User,
    user_with_no_access: models.User,
) -> models.User | None:
    """Fixture to parametrize user."""
    mapping = {
        "anon": None,
        "user_with_access_to_files": user_with_access_to_files,
        "user_with_access_to_special_file": user_with_access_to_special_file,
        "user_with_no_access": user_with_no_access,
    }
    return mapping[request.param]


@pytest.fixture(scope="session")
def model_with_files(django_db_blocker) -> models.ModelWithFiles:
    """Create user with access to files."""
    with django_db_blocker.unblock():
        return factories.ModelWithFilesFactory()  # type: ignore
