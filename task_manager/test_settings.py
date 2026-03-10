from .settings import *

SECRET_KEY = "django-insecure-test-only-key-2026"
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}