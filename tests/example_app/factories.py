import uuid

import factory

from . import models

DEFAULT_PASSWORD = "Test111!"


class Email(factory.LazyAttribute):
    """Generate email."""

    def __init__(self) -> None:
        super().__init__(
            function=lambda obj: (f"{uuid.uuid4()}@" f"drf-s3-direct.com"),
        )


class UserFactory(factory.django.DjangoModelFactory):
    """Factory to generate test User instance."""

    email = Email()
    username = factory.Faker("user_name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall(
        "set_password",
        DEFAULT_PASSWORD,
    )

    class Meta:
        model = models.User


class ModelWithFilesFactory(factory.django.DjangoModelFactory):
    """Factory to generate test ModelWithFiles instance."""

    file = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    private_file = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    quick_expire_file = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    all_file_types = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    all_file_sizes = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    anon_files = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    small_file = factory.django.FileField(
        filename="file.txt",
        data="Test",
    )
    image = factory.django.ImageField(
        color="magenta",
    )

    class Meta:
        model = models.ModelWithFiles
