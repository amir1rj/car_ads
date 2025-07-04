import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!80r%debx%y5qj^6v*4!lvi@ssp5@zv4^*a&&r4s^9ho-jy09)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["https://dolox.ir", "https://admin.dolox.ir",
                        'http://158.255.74.78:8000', 'http://158.255.74.78']

# Application definition

INSTALLED_APPS = [
    'daphne',
    "haystack",
    'drf_spectacular',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    # apps
    'account.apps.AccountConfig',
    'ads.apps.AdsConfig',
    'chat.apps.ChatConfig',
    "auction.apps.AuctionConfig",
    "notification.apps.NotificationConfig",
    'finance.apps.FinanceConfig',
    # third party
    'storages',
    'django_celery_results',
    'django_celery_beat',
    'django_user_agents',
    # 'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]
# INTERNAL_IPS = [
#     '127.0.0.1',
#     '172.20.0.4',
#     '172.20.0.1'
# ]
# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK": lambda request: True,
# }
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     # 'debug_toolbar.panels.time.TimePanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     # سایر پنل‌ها
# ]
ROOT_URLCONF = 'car_ads.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
ASGI_APPLICATION = "car_ads.asgi.application"
# WSGI_APPLICATION = 'car_ads.wsgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'car_ads_db',
        'USER': 'root',
        'PASSWORD': 'amir1234amir',
        'HOST': 'postgres',
        'PORT': '5432',
        'OPTIONS': {
            "server_side_binding": True,
        },
    }
}
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

TOKEN_LIFESPAN = 5  # in minutes
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(STATIC_URL, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "media/"
REST_FRAMEWORK = {
    # YOUR SETTINGS
    'EXCEPTION_HANDLER': 'account.exceptions.custom_exception_handler',

    'DEFAULT_PAGINATION_CLASS': 'ads.pagination.CustomPagination',
    'PAGE_SIZE': 6,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (

        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "account.User"

SPECTACULAR_SETTINGS = {
    'TITLE': 'car_ads API',
    'DESCRIPTION': 'an API doc for car_ads project',
    'VERSION': '1.0.0',

    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [
        {
            'BearerAuth': [],
        },
    ],
    'AUTHENTICATION_WHITELIST': ['rest_framework_simplejwt.authentication.JWTAuthentication'],
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
}
PAGINATION_PAGE_SIZE = 6
LOCALE_PATHS = os.path.join(BASE_DIR, 'locale/'),

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30)
}
# arvan cloud storages
DEFAULT_FILE_STORAGE = "storages.backends.s3.S3Storage"
AWS_S3_ACCESS_KEY_ID = 'b9189c7f-1727-4604-ba04-71d2a053857d'
AWS_S3_SECRET_ACCESS_KEY = '96df442355aee0f2b73e429f56f3d3523256696816560f9ad0d098149a2db449'
AWS_S3_ENDPOINT_URL = 'https://s3.ir-tbz-sh1.arvanstorage.ir'
AWS_STORAGE_BUCKET_NAME = 'django-car-ads'
# AWS_QUERYSTRING_AUTH = False
AWS_SERVICE_NAME = 's3'
AWS_S3_FILE_OVERWRITE = False
# haystack
WHOOSH_INDEX = os.path.join(BASE_DIR, 'whoosh/')
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': WHOOSH_INDEX,
        'TOKENIZER': 'haystack.analysis.PersianAnalyzer',
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
# celery😗
CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_IMPORTS = [
    'account.tasks',
    'auction.tasks',
]

MERCHANT = '4dc2a7fd-aa4f-420d-9405-9428edf4d718'
DOMAIN = '127.0.0.1'
