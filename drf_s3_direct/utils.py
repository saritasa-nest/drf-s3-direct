import os
import unicodedata
import uuid


def remove_special_characters(filename: str) -> str:
    """Remove characters from filename that are not allowed in different OS."""
    special_characters = r"<>:\"/\\|?*"
    return filename.translate({ord(i): None for i in special_characters})


def normalize_string_value(value: str) -> str:
    """Normalize string value.

    1. Remove leading and trailing whitespaces.
    2. Replace all space characters with the Space char.
    3. Normalize Unicode string using `NFKC` form. See the details:
    https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize

    """
    cleaned = " ".join(value.strip().split()).strip()
    return unicodedata.normalize("NFKC", cleaned)


def clean_filename(filename: str) -> str:
    """Remove `garbage` characters that cause problems with file names."""
    cleaned = remove_special_characters(filename)
    normalized = normalize_string_value(cleaned)

    return normalized


def get_random_filename(filename: str) -> str:
    """Get random filename.

    Generation random filename that contains unique identifier and
    filename extension like: ``photo.jpg``.

    If extension is too long (we had issue with that), replace it with
    special ".extension".

    Args:
        filename (str): Name of file.

    Returns:
        new_filename (str): ``9841422d-c041-45a5-b7b3-467179f4f127.ext``.

    """
    path = str(uuid.uuid4())
    ext = os.path.splitext(filename)[1].lower()
    if len(ext) > 15:
        ext = ".incorrect"

    return "".join((path, ext))
