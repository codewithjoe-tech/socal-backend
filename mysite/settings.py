
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os


load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-^$n@v9z)i#$c)r95wqm*$0@pwx9tx-v3u26i&5w-k+c-_wt(^r'


DEBUG = True

ALLOWED_HOSTS = []



INSTALLED_APPS = [
    "corsheaders",
    "daphne",
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    # External Apps
    'rest_framework_simplejwt',
    'rest_framework',
    'django_celery_beat',
    "storages",

    # Internal Apps
    'UserManagement',
    "Profiles",
    "AdminPanel",
    'ReportApp',
    "Chat"


]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'Profiles': {  
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 7000

CSRF_TRUSTED_ORIGINS = ['http://localhost:5173']
DATASET_DIR = os.path.join(BASE_DIR, 'data')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

AUTH_USER_MODEL = 'UserManagement.User'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
     "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOW_ALL_ORIGINS=True
ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

AUTHENTICATION_BACKENDS = [
    'UserManagement.custom_authenticate.EmailorUsernameValidate',
    'django.contrib.auth.backends.ModelBackend',
]

WSGI_APPLICATION = 'mysite.wsgi.application'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY =os.getenv('AWS_SECRET_ACCESS_KEY')



AWS_STORAGE_BUCKET_NAME = 'friendbook-bkt'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' %AWS_STORAGE_BUCKET_NAME
AWS_S3_FILE_OVERWRITE = False
STORAGES = {

    "default": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
    
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR/'static'
]

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR/'media'

# Channels settings

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

ASGI_APPLICATION ='mysite.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'codewithjoe16@gmail.com'
EMAIL_HOST_PASSWORD = 'uhwj zzog jevi qryv'