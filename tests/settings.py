DEBUG = True
TESTING = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SECRET_KEY = "testingsecretkey"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_database',
    }
}

CELERY_TASK_ALWAYS_EAGER = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "tests",
    "ariadne_extended.graph_loader",
    "ariadne_extended.cursor_pagination",
    "ariadne_extended.uuid",
    "ariadne_extended.payload",
]
