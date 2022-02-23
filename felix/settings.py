"""
Django settings for felix project.

"""
import os

import environ


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

root = environ.Path(BASE_DIR)
env = environ.Env(
    ENVIRONMENT_NAME=(str, 'test'),
    DEBUG=(bool, False),

    USE_AZURE=(bool, True),
    SSL_REDIRECT=(bool, False),

    FIRST_COMPANY_DEFAULT=(bool, False),

    # If True, Celery tasks are executed like functions in the FG and not queued
    CELERY_SYNC_TASKS=(bool, False),

    ASSET_ID=(str, 'default'),

    DOMAIN=(str, 'localhost:8002'),
)
environ.Env.read_env(root('felix/.env'))

SITE_ROOT = root()

DOMAIN = env('DOMAIN')

# Databases
DATABASES = {
    'default': env.db(),
}

# To avoid warnings. New in Django 3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Caches
CACHES = {
    'default': env.cache()
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = env('DEBUG')  # False if not in os.environ
DEBUG = False

COMPANY_ID = env('COMPANY_ID')

ALLOWED_HOSTS = ['*']

SECURE_SSL_REDIRECT = env('SSL_REDIRECT')
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'storages',
    'crispy_forms',
    'django_js_reverse',
    'rolepermissions',
    'anymail',
    'urlshortening',
    'tinymce',

    'rest_framework',
    'rest_framework.authtoken',

    'insurers',
    'motorinsurance_shared',

    'core',
    'accounts',
    'customers',
    'motorinsurance',

    'auto_quoter',
    'mortgage',
    'mortgagequote',
]

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'core.middleware.AjaxRedirectMiddleware',
    'core.middleware.CompanyMiddleware',
    'core.middleware.RemoteAddressMiddleware',
    'core.middleware.WorkSpaceMiddleware',

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

ROOT_URLCONF = 'felix.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'felix.context_processors.settings_processor',
                'felix.context_processors.override_css',
            ],
        },
    },
]

WSGI_APPLICATION = 'felix.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
    {
        'NAME': 'core.validators.MaximumLengthValidator'
    }
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dubai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_AZURE = env('USE_AZURE')

AWS_S3_REGION_NAME = env('AWS_DEFAULT_REGION')
AWS_S3_FILE_OVERWRITE = False

PUBLIC_S3_BUCKET = env('PUBLIC_S3_BUCKET')
PUBLIC_BUCKET_CDN_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')

PRIVATE_S3_BUCKET = env('PRIVATE_S3_BUCKET')

AIRTABLE_API_KEY = env('AIRTABLE_API_KEY')
DOCRAPTOR_API_KEY = env('DOCRAPTOR_API_KEY')

ROLEPERMISSIONS_MODULE = 'accounts.roles'

AZURE_STORAGE_KEY = env('AZURE_STORAGE_KEY')
AZURE_STORAGE_ACCOUNT_NAME = env('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_SHARED_TOKEN = env('AZURE_STORAGE_SHARED_TOKEN')

if USE_AZURE:
    STATICFILES_STORAGE = 'felix.storages.PublicAzureStorage'
    DEFAULT_FILE_STORAGE = 'felix.storages.PrivateAzureStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

ASSET_ID = env('ASSET_ID')

STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'common_static'),
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

JS_REVERSE_EXCLUDE_NAMESPACES = ['admin', 's3direct', 'accounts', 'insurers']
JS_REVERSE_OUTPUT_PATH = os.path.join(BASE_DIR, 'common_static', 'js')
JS_REVERSE_JS_MINIFY = False
JS_REVERSE_JS_VAR_NAME = 'DjangoUrls'

# If this is True, then on the pages that get the company record from the (sub)domain, if the given host doesn't match
# any known company, we default to using the first Company record. This is for ease of development so we don't have
# to configure hosts on every environment
FIRST_COMPANY_DEFAULT = env('FIRST_COMPANY_DEFAULT')

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_TASK_ALWAYS_EAGER = env('CELERY_SYNC_TASKS')
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'region': env('AWS_DEFAULT_REGION'),
    'visibility_timeout': 300,  # Max 5 minutes before a task is considered dead
    'polling_interval': env('SQS_POLLING_INTERVAL'),
    'queue_name_prefix': env('CELERY_QUEUE_PREFIX'),
}

# TWILIO_SID = env('TWILIO_SID')
# TWILIO_TOKEN = env('TWILIO_TOKEN')
# TWILIO_NUMBER = env('TWILIO_NUMBER')

INITIAL_URL_LEN = 5
RETRY_COUNT = 5
REDIRECT_PREFIX = 'r'

DEFAULT_FROM_EMAIL = env('EMAIL_FROM')

EMAIL_CONFIGURATION = {
    'mailgun': {
        'password': env('MAILGUN_API_KEY'),
        'api_url': f'https://api.mailgun.net/v3/{env("MAILGUN_SENDER_DOMAIN")}'
    },
    'sendgrid': {
        'api_key': env('SENDGRID_API_KEY')
    }
}

POSTMARK_TOKEN = env('POSTMARK_TOKEN')

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": POSTMARK_TOKEN,
}

EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'

AUTO_QUOTERS = {
    'drools': env('AUTO_QUOTER_DROOL_URL'),
    'qic': {
        'base_url': env('AUTO_QUOTER_QIC_URL'),
        'model_code_mapping_file': root('auto_quoter/api_mappings/qic/models.csv')
    },
    'tokio_marine': {
        'vehicle_mapping_file': root('auto_quoter/api_mappings/tokiomarine/vehicles.csv')
    },
    'oic': {
        'api_url': env('AUTO_QUOTER_OIC_API_URL', default='https://api.tameen.ae/personal/motor/v1'),
        'login_url': env('AUTO_QUOTER_OIC_LOGIN_URL', default='https://login.tameen.ae/connect/token')
    },
    'dnirc': {
        'api_url': env('AUTO_QUOTER_DNIRC_API_URL'),
    },
    'alittihad': {
        'api_url': env('AUTO_QUOTER_ALITTIHAD_API_URL'),
    },
    'watania': {
        'api_url': env('AUTO_QUOTER_WATANIA_API_URL'),
    },
    'al ain ahlia': {
        'api_url': env('AUTO_QUOTER_AL_AIN_API_URL'),
    },
    'al sagr': {
        'api_url': env('AUTO_QUOTER_AL_SAGR_API_URL'),
    },
    'aman': {
        'api_url': env('AUTO_QUOTER_AMAN_API_URL'),
    }
}

ALGOLIA = {
    'APPLICATION_ID': env('ALGOLIA_APP_ID'),
    'API_KEY': env('ALGOLIA_API_KEY'),
    'SEARCH_API_KEY': env('ALGOLIA_SEARCH_API_KEY'),
    'ENV': env('ALGOLIA_ENV'),
}

AMPLITUDE = {
    'API_KEY': env('AMPLITUDE_API_KEY')
}

DOC_PARSER = {
    'API_KEY': env('DOC_PARSER_API_KEY')
}

ALGODRIVEN = {
    'API_KEY': env('ALGODRIVEN_API_KEY')
}

INTERCOM = {
    'APP_ID': env('INTERCOM_APP_ID'),
    'SECRET_KEY': env('INTERCOM_SECRET_KEY'),
    'ACCESS_TOKEN': env('INTERCOM_ACCESS_TOKEN'),
}

TINYMCE_DEFAULT_CONFIG = {
    'theme_advanced_buttons1': 'bold,italic,underline,link,bullist'
}
TINYMCE_JS_URL = 'https://felix-public-20180921204519404200000001.s3-eu-west-1.amazonaws.com/tiny_mce/tiny_mce.js'

ENVIRONMENT = env('ENVIRONMENT_NAME')

INTERNAL_IPS = [
    '127.0.0.1',
]
if not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
if not DEBUG:
    sentry_sdk.init(
        environment=env('ENVIRONMENT_NAME'),
        dsn=env('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        send_default_pii=True,

        traces_sample_rate=0.75
    )

_1mb = 1024 * 1024
LOG_DIR = env('LOG_DIR')
CSRF_TRUSTED_ORIGINS = ['https://crm1.insurenex.io']
CORS_ORIGIN_WHITELIST = ('https://crm1.insurenex.io',)
CSRF_COOKIE_DOMAIN = ".crm1.insurenex.io"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] [%(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'django': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'maxBytes': _1mb * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },

        'api': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'api.log'),
            'maxBytes': _1mb * 50,
            'backupCount': 10,
            'formatter': 'verbose',
        },

        'auto_quote': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'auto_quote.log'),
            'maxBytes': _1mb * 50,
            'backupCount': 100,
            'formatter': 'verbose',
        },

        'user_actions': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'user.actions.log'),
            'maxBytes': _1mb * 50,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'workers': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'workers.log'),
            'maxBytes': _1mb * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        # Ignore DisallowedHost errors as we throw them ourselves
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },

        'django': {
            'handlers': ['django', 'console'],
            'level': 'INFO',
        },

        'api': {
            'handlers': ['api', 'console'],
            'level': 'DEBUG'
        },

        'auto_quote': {
            'handlers': ['auto_quote', 'console'],
            'level': 'DEBUG'
        },

        'user_actions': {
            'handlers': ['user_actions', 'console'],
            'level': 'INFO'
        },
        'user_facing': {
            'handlers': ['django'],
            'level': 'INFO'
        },
        'workers': {
            'handlers': ['workers', 'console'],
            'level': 'INFO'
        },
        'security': {
            'handlers': ['django', 'console'],
            'level': 'WARNING'
        },
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    },
}
