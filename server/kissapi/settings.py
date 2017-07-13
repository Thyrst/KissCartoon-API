import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u%*#7=f35^a8aytf*k8#8n(k8h&)24c&pj#pbe6!o&b39x#vww'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ORIGINAL_SITE = os.getenv('KISSAPI_ORIGINAL_SITE', 'kisscartoon.io')
HOST = os.getenv('KISSAPI_HOSTNAME', 'localhost')

ALLOWED_HOSTS = ['127.0.0.1', HOST]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',

    'rest_framework'
]

ROOT_URLCONF = 'kissapi.urls'

WSGI_APPLICATION = 'kissapi.wsgi.application'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
    )
}

CACHE = {'updated': None, 'data': None}
