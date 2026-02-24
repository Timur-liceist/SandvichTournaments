import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from django.urls import reverse_lazy
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка env окружения
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "true") in ["true", "True"]
print("DEBUG", DEBUG)
print("SECRET_KEY", SECRET_KEY)
ALLOWED_HOSTS = [
    "*",
]
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
# Добавляем домен Render
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    ALLOWED_HOSTS.append("https://" + RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS = [f"https://{RENDER_EXTERNAL_HOSTNAME}"]


# URL, по которому будет доступна статика
STATIC_URL = "/static/"

# Папка, куда collectstatic будет собирать файлы (должна совпадать с путями в docker-compose)
STATIC_ROOT =  BASE_DIR / "staticfiles"

# Дополнительно: где лежат исходные статики в приложениях
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Ваша текущая папка static
]

# Для загружаемых пользователями файлов
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


INSTALLED_APPS = [
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # libraries apps
    "widget_tweaks",
    "mdeditor",
    "social_django",
    # my apps
    "users",
    "news",
    "teams",
    "tournaments",
    "core",
]

TIME_LIMITE_FOR_REQUEST_TOURNAMENT = timedelta(hours=3)
TIME_INTERVAL_INVITE_USER_TO_TEAM = timedelta(hours=24)

# Путь к директории логов (можно изменить)
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Создаем директорию, если её нет
os.makedirs(LOG_DIR, exist_ok=True)

# Формат имени файла: logs/app-2025-04-05.log
LOG_FILE = os.path.join(
    LOG_DIR, f'app-{datetime.now().strftime("%Y-%m-%d")}.log'
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} \
                {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE,
            "when": "midnight",  # Ротация каждый день в полночь
            "interval": 1,
            "backupCount": 30,  # Хранить 30 файлов (30 дней)
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "myapp": {  # Замени 'myapp' на имя своего приложения или используй любое другое
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Настройки Celery
# CELERY_BROKER_URL = (
#     "redis://redis:6379/0"  # Адрес сервиса redis из docker-compose
# )
# CELERY_RESULT_BACKEND = (
#     "redis://redis:6379/0"  # Где хранить результаты задач (опционально)
# )
# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = "Europe/Moscow"  # Или ваш часовой пояс

STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
STEAM_ID_REGEX = re.compile(r"https://steamcommunity.com/openid/id/(\d+)")
OPENID_URL = "https://steamcommunity.com/openid/"
AUTHENTICATION_BACKENDS = (
    "social_core.backends.steam.SteamOpenId",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_STEAM_API_KEY = "4DAEB2E91DC5D90F84BC8662AC8F88C3"

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    # ❌ Убираем social_user, create_user и associate_user,
    # ❌ чтобы user никогда не создавался.
    # 'social_core.pipeline.social_auth.social_user',
    # 'social_core.pipeline.user.get_username',
    # 'social_core.pipeline.user.create_user',
    # 'social_core.pipeline.social_auth.associate_user',
    "social_core.pipeline.social_auth.load_extra_data",
    # наш кастомный шаг — перенаправить куда нужно
    "users.pipeline.redirect_with_steam_id",
)
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.load_extra_data",
    "users.pipeline.redirect_with_steam_id",
)


LOGIN_REDIRECT_URL = "/steam-auth-complete/"
LOGOUT_REDIRECT_URL = "/"


ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
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

WSGI_APPLICATION = "django_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
LOGIN_URL = reverse_lazy("users:need_auth_steam")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"


STATICFILES_DIRS = [
    Path(BASE_DIR) / "static",
]

STATIC_ROOT = Path(BASE_DIR) / "staticfiles"


MEDIA_URL = "/media/"
MEDIA_ROOT = Path(BASE_DIR) / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.UserModel"

MDEDITOR_CONFIGS = {
    "default": {
        "width": "90% ",  # Custom edit box width
        "height": 500,  # Custom edit box height
        "toolbar": [
            "undo",
            "redo",
            "|",
            "bold",
            "del",
            "italic",
            "quote",
            "ucwords",
            "uppercase",
            "lowercase",
            "|",
            "h1",
            "h2",
            "h3",
            "h5",
            "h6",
            "|",
            "list-ul",
            "list-ol",
            "hr",
            "|",
            "link",
            "image",
            "table",
            "datetime",
            "emoji",
            "html-entities",
            "pagebreak",
            "goto-line",
            "|",
            "help",
            "info",
            "||",
            "preview",
            "watch",
            "fullscreen",
        ],  # custom edit box toolbar
        "upload_image_formats": [
            "jpg",
            "jpeg",
            "gif",
            "png",
            "bmp",
            "webp",
        ],
        "image_folder": "editor",  # image save the folder name
        "theme": "default",  # edit box theme, dark / default
        "preview_theme": "default",  # Preview area theme, dark / default
        "editor_theme": "default",  # edit area theme, pastel-on-dark / default
        "toolbar_autofixed": True,  # Whether the toolbar capitals
        "search_replace": True,  # Whether to open the search for replacement
        "emoji": True,  # whether to open the expression function
        "tex": True,  # whether to open the tex chart function
        "flow_chart": True,  # whether to open the flow chart function
        "sequence": True,  # Whether to open the sequence diagram function
        "watch": True,  # Live preview
        "lineWrapping": False,  # lineWrapping
        "lineNumbers": False,  # lineNumbers
        "language": "en",  # zh / en / es
    },
}
