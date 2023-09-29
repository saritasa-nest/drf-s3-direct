import os

ALLOWED_HOSTS = ["*"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = "a87082n4v52u4rnvk2edv128eudfvn5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_probes",
    "django_extensions",
    "drf_s3_direct",
    "tests.example_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tests.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 600,
        "USER": "drf-s3-direct-user",
        "NAME": "drf-s3-direct-dev",
        "PASSWORD": "postgres",
        "HOST": "postgres",
        "PORT": 5432,
    },
}

AUTH_USER_MODEL = "example_app.User"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
AWS_IS_MINIO = True
AWS_S3_ACCESS_KEY_ID = "root"
AWS_S3_SECRET_ACCESS_KEY = "rootroot"
AWS_S3_ENDPOINT_URL = "http://minio:9001"
AWS_STORAGE_BUCKET_NAME = "drf-s3-direct-files"
AWS_QUERYSTRING_AUTH = False

DRF_S3_DIRECT_DEFAULT_FILE_PERMISSION = (
    "tests.example_app.api.permissions.CheckPermissionToFile"
)
DRF_S3_DIRECT_FILE_PERMISSION_MAPPING = {
    "example_app.modelwithfiles.image": (
        "tests.example_app.api.permissions.CheckPermissionToSpecialFile"
    ),
}
