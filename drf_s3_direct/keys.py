import abc
import uuid

from . import utils


class S3Key:
    """Base class for s3 keys."""

    @abc.abstractmethod
    def __call__(self, filename: str | None) -> str:
        """Abstract method for calling keys."""


class S3KeyWithUUID(S3Key):
    """Prefixed key generator."""

    def __init__(self, prefix: str) -> None:
        self.prefix: str = prefix

    def __call__(self, filename: str | None) -> str:
        """Return prefixed S3 key."""
        if not filename:
            return f"{self.prefix}/{uuid.uuid4()}.incorrect"
        return f"{self.prefix}/{utils.get_random_filename(filename)}"


class S3KeyWithPrefix(S3Key):
    """Class to create S3 key for destination."""

    def __init__(self, prefix: str) -> None:
        self.prefix: str = prefix

    def __call__(self, filename: str) -> str:  # type: ignore[override]
        """Create key for destination using filename."""
        return f"{self.prefix}/{uuid.uuid4()}/{utils.clean_filename(filename)}"
