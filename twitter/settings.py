"""
Django settings for twitter project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from kombu import Queue
from pathlib import Path
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'li5n-2i4%43%j)%&i$&rx1aq)o^bzv5-_@+x8)&j%(sg)gl^qa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '192.168.1.8', 'localhost']

INTERNAL_IPS = ['127.0.0.1', '192.168.1.8', 'localhost']
# Application definition

INSTALLED_APPS = [
    # django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party packages
    'rest_framework',
    "debug_toolbar",
    'django_filters',
    'notifications',

    # project apps
    'accounts', # we did not add this previously because there is no model in it
    'tweets',
    'friendships',
    'newsfeeds',
    'comments',
    'likes',
    'inbox',
]

DEFAULT_AUTO_FIELD='django.db.models.AutoField'
# Django upgraded as django-notification installed
# To supress warning messages about Auto-created primary key
# We need to add this line

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    # Settings for django_filters
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],

    'EXCEPTION_HANDLER': 'utils.ratelimit.exception_handler',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'twitter.urls'

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

WSGI_APPLICATION = 'twitter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'twitter',
        'HOST': '0.0.0.0',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'yourpassword', 
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Normally we don't want to put the file into the base directory of the project
# Then we need to define the MEDIA_ROOT
# Try again after you defined this.
# MEDIA_ROOT = BASE_DIR / 'media'
# Commented this because django storage deployed

# Then adding MEDIA_URL to allow the user to access the media files
# MEDIA_URL = '/media/'
#
# Not recommended in production!
# We want the web server to be stateless
# which means it should not preserve files
# When the server is died, the files can still be accessed.
#
# One step further: Can we directly use DB to store files?
# Don't do that. DB should only store structured data rather than blob files.
# Normally we store the files in the AWS s3 or Azure blob storage

# So, here we use django-storage to link AWS s3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
TESTING = ((" ".join(sys.argv)).find('manage.py test') != -1) 
# This will allow django to know it is the test env now.
# python manage.py test
if TESTING:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    # Why do this?
    # 1. To save the time of the unit time
    # 2. Causing unexpected error due to the 3rd party 
    # That's why Unit test should not have external dependencies such as AWS
AWS_STORAGE_BUCKET_NAME = 'django-twitter'
AWS_S3_REGION_NAME = 'ap-tokyo-1'
# Also, you need to add the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
AWS_S3_ENDPOINT_URL = 'https://nrzfbjgus5of.compat.objectstorage.ap-tokyo-1.oraclecloud.com'
AWS_ACCESS_KEY_ID = os.getenv('ORACLE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('ORACLE_SECRET_ACCESS_KEY')


# Use `apt install memcached` and `pip install python-memcached` to fully support memcached
# For more info, see https://docs.djangoproject.com/en/3.1/topics/cache/
# Don't use `pip install memcache` or django-memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,   #TTL: time to live
    },
    'testing': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'testing',
    },
    'ratelimit': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400 * 7,
        'KEY_PREFIX': 'rl',
    }
}


# FOR Redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0 if TESTING else 1
# DB names of Redis are integer, there is no character-based names for it
REDIS_KEY_EXPIRE_TIME = 3600 * 24 * 7
REDIS_LIST_LENGTH_LIMIT = 100 if not TESTING else 20

# Celery
CELERY_BROKER_URL = 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, "2") \
                    if not TESTING else 'redis://{}:{}/{}'.format(REDIS_HOST, REDIS_PORT, "0")
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_ALWAYS_EAGER = TESTING
# CELERY_TASK_ALWAYS_EAGER is very important.
# = TESTING means it will run task in sync during unit test
CELERY_QUEUE = (
    Queue('default', routing_key='default'),
    Queue('newsfeeds', routing_key='newsfeeds'),
) 
# CELERY_QUEUE and routing_key: put tasks into different queues based to distinguish its priority.
# Same frequency to launch async tasks in each queue: 
# default -> newsfeeds -> default -> newsfeeds -> ...
# In async task functions, use routing_key in shared_task to assign queue.
# 
# Why? 1 million follower problem:
# - Supposed we have 100 workers and batch size is 100
# - equals a worker have 100 tasks pending to process, suppose it takes 10 minutes
# Such heavy workload will take up plenty of resources and some urgent tasks could comes...
# - at this time, a user want to sign up your site and wait for SMS verification
# - it could take 10 minutes+ wait for them since there is no worker left.

## Further more, I would like to assign some workers to higher priority tasks and some execute lowers:
# import os
# from dotenv import load_dotenv
# load_dotenv()
# if os.getenv('WORKER_TYPE') == 'newsfeeds':
#     CELERY_QUEUE = (
#         Queue('newsfeeds', routing_key='newsfeeds'),
#     ) 
# else:
#     CELERY_QUEUE = (
#         Queue('default', routing_key='default'),
#     ) 

# DUPLICATED: for learning
if os.getenv('WORKER_TYPE') == 'everything':
    CELERY_QUEUE = (
        Queue('default', routing_key='default'),
        Queue('newsfeeds', routing_key='newsfeeds'),
    ) 

# Celery can be directly executed using command line for workers:
#   celery -A twitter worker -l info


# Rate Limit
RATELIMIT_USER_CACHE = 'ratelimit'
RATELIMIT_CACHE_PREFIX = 'rl:' # You can also delete this line and use the prefix above
RATELIMIT_ENABLE = not TESTING

# # You can also...
# if os.getenv('ENVIRONMENT') == 'DEV':
#     RATELIMIT_ENABLE = False


# HBase
HBASE_HOST = '127.0.0.1'

# This is how to import local settings in django
try:
    from .local_settings import *
    # Normally, for the best practice, don't use import * for performance
    # But you can use it here since it is a local setting file
    # Since you need all the settings 
except:
    pass