import dj_database_url as db

DEBUG = True
TESTING = True

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

SECRET_KEY = "testingsecretkey"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        **db.config(default="postgres://127.0.0.1:5432/ariadne_extended"),
    }
}

CELERY_TASK_ALWAYS_EAGER = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "waffle",
    "tests",
    "tests.pagination",
    "ariadne_extended.graph_loader",
    "ariadne_extended.cursor_pagination",
    "ariadne_extended.uuid",
    "ariadne_extended.payload",
    "ariadne_extended.contrib.waffle_graph",
]

WAFFLE_FLAG_DEFAULT = False
WAFFLE_SWITCH_DEFAULT = False
WAFFLE_SAMPLE_DEFAULT = True
