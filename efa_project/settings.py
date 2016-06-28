# -*- encoding: utf-8 -*-
"""
Django settings for correctiv_eurosfueraerzte project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import re

import dj_database_url
import django_cache_url

from django.utils.translation import ugettext_lazy as _

get_env = lambda x, y=None: os.environ.get(x, y)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ADMINS = (
    ('Stefan Wehrmeyer', 'stefan.wehrmeyer@correctiv.org'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('DJANGO_SECRET_KEY', 'secret-key-4124')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env('DJANGO_DEBUG', 'false') == 'true'

ALLOWED_HOSTS = [get_env('DJANGO_ALLOWED_HOSTS', '*')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.postgres',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    'sekizai',  # for javascript and css management

    'correctiv_eurosfueraerzte',
    # 'geogermany',

]


MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'efa_project.urls'


WSGI_APPLICATION = 'efa_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

_default_db = dj_database_url.config(
    env='DATABASE_URL',
    default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
)

if 'postgresql' in _default_db['ENGINE']:
    _default_db['CONN_MAX_AGE'] = 600

DATABASES = {
    'default': _default_db,
}
POSTGIS_VERSION = (2, 1, 5)

CACHES = {'default': django_cache_url.config()}


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
    ),
    'DEFAULT_PERMISSION_CLASSES': (
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

CORS_ORIGIN_WHITELIST = (
    'correctiv.github.io',
    'apps.correctiv.org',
)
CORS_ORIGIN_REGEX_WHITELIST = ('^http://localhost(:\d+)?$', )
CORS_URLS_REGEX = r'^/api/.*$'

TIME_ZONE = 'Europe/Berlin'

DATE_FORMAT = "d. F Y"
SHORT_DATE_FORMAT = "d.m.Y"
DATE_INPUT_FORMATS = ("%d.%m.%Y",)
SHORT_DATETIME_FORMAT = "d.m.Y H:i"
DATETIME_INPUT_FORMATS = ("%d.%m.%Y %H:%M"),
TIME_FORMAT = "H:i"
TIME_INPUT_FORMATS = ("%H:%M",)

USE_TZ = True

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = (
    os.path.abspath(os.path.join(BASE_DIR, 'locale')),
)

LANGUAGE_CODE = 'de'

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'main': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "public", "static")

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, "public", "media"))
MEDIA_URL = get_env('MEDIA_URL', '/media/')

# Additional locations of static files
STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

_TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, "efa_project", "templates"),
]

_TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

if not DEBUG:
    _TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader', _TEMPLATE_LOADERS),
    ]


_TEMPLATE_CONTEXT_PROCESSORS = [
    'django.template.context_processors.i18n',
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.template.context_processors.media',
    'django.template.context_processors.csrf',
    'django.template.context_processors.tz',
    'sekizai.context_processors.sekizai',
    'django.template.context_processors.static',
    'correctiv_eurosfueraerzte.context_processors.cms_shim'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': _TEMPLATE_DIRS,
        # 'APP_DIRS': True,
        'OPTIONS': {
            'loaders': _TEMPLATE_LOADERS,
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS,
            'debug': DEBUG
        },
    },
]

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
            "break-on-newline": True,
            "wiki-tables": True
        },
        "safe_mode": "escape",
    },
    "community": {
        "extras": {
            "code-friendly": None,
            "break-on-newline": True,
            "link-patterns": None
        },
        "link_patterns": [
            (re.compile(r"\b([\w_\.\-\+]+@[\w\.\-]+\.\w+)\b", re.I),
             r"mailto:\1"),
            (re.compile(r"@(\w+)\b", re.I),
             r"https://twitter.com/\1"),
            (re.compile(r"(?:^|[^\B\"])(https?://[^\s\<]*)", re.I),
             r"\1"),
        ],
        "safe_mode": "escape",
    },
    "comments": {
        "extras": {
            "break-on-newline": True,
            "link-patterns": None
        },
        "link_patterns": [
            (re.compile(r"@(\d+)\b", re.I),
             r"#comment-\1"),
            (re.compile(r"(?:^|[^\B\"])(https?://\S*)", re.I),
             r"\1"),
        ],
        "safe_mode": "escape",
    },
}


CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    'STATIC_URL': STATIC_URL
}

META_SITE_PROTOCOL = 'https'
META_USE_SITES = True

SITE_URL = get_env('SITE_URL', 'https://correctiv.org')
SITE_NAME = get_env('SITE_NAME', 'CORRECTIV')

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (6.0, 45.0),
    'DEFAULT_ZOOM': 14,
    'MIN_ZOOM': 1,
    'MAX_ZOOM': 20,
    'TILES': 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
    'SCALE': None,
    'ATTRIBUTION_PREFIX': '<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a> contributors <a href="https://cartodb.com/attributions">© CartoDB</a>, CartoDB <a href="https://cartodb.com/attributions">attribution</a',
}


try:
    from .local_settings import *  # noqa
except ImportError:
    pass

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
