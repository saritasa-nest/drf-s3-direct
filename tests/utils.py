from django.urls import reverse_lazy


def get_s3_params_url() -> str:
    """Get url to s3 params endpoint."""
    return reverse_lazy("drf-s3-direct-get-params")


def get_download_url(
    app: str,
    model: str,
    pk: str | int,
    field: str,
) -> str:
    """Get url to downloading s3 file."""
    return reverse_lazy(
        "drf-s3-direct-get-file",
        kwargs={
            "app": app,
            "model": model,
            "pk": pk,
            "field": field,
        },
    )
