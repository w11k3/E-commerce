"""
Django settings for app project.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


# ==========================================================
# CAMINHOS DO PROJETO
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================================
# SEGURANÇA
# ==========================================================

DEBUG = os.environ.get("DJANGO_DEBUG", "True").strip().lower() in {
    "true", "1", "yes"
}

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Configure a variável de ambiente DJANGO_SECRET_KEY."
        )

    # Somente para desenvolvimento local.
    SECRET_KEY = (
        "voad-dev-local-only-7$k9!Q2@xP4#zR8^mN6&bT1"
    )

# Libera acessos do localhost e domínios do Ngrok
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,*.ngrok-free.app,*.ngrok-free.dev,*"
    ).split(",")
    if host.strip()
]

# Permite envios de formulários/login (CSRF) através do Ngrok
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Configure DJANGO_ALLOWED_HOSTS com o domínio do site."
    )


# Proteções aplicadas quando DEBUG=False.
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# ==========================================================
# APLICATIVOS
# ==========================================================

INSTALLED_APPS = [
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "products",
    "cart",
    "orders",
]


# ==========================================================
# MIDDLEWARE
# ==========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================================================
# URLS E TEMPLATES
# ==========================================================

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "products.context_processors.loja",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# ==========================================================
# BANCO DE DADOS
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==========================================================
# AUTENTICAÇÃO E SENHAS
# ==========================================================

AUTH_USER_MODEL = "accounts.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ==========================================================
# INTERNACIONALIZAÇÃO
# ==========================================================

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Campo_Grande"

USE_I18N = True

USE_TZ = True


# ==========================================================
# ARQUIVOS ESTÁTICOS
# ==========================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# ==========================================================
# ARQUIVOS DE MÍDIA
# ==========================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# E-MAIL
# ==========================================================

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")

EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))

EMAIL_USE_TLS = os.environ.get(
    "EMAIL_USE_TLS", "True"
).strip().lower() in {"true", "1", "yes"}

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")

EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "noreply@voad.local",
)


# ==========================================================
# JAZZMIN — PAINEL ADMINISTRATIVO
# ==========================================================

JAZZMIN_SETTINGS = {
    "site_title": "VOAD | Administração",
    "site_header": "VOAD",
    "site_brand": "VOAD",
    "welcome_sign": "Painel administrativo da VOAD",
    "copyright": "VOAD",

    "show_ui_builder": False,
    "language_chooser": False,
    "show_sidebar": True,
    "navigation_expanded": True,

    "order_with_respect_to": [
        "accounts",
        "products",
        "cart",
        "orders",
        "auth",
    ],

    "icons": {
        "accounts": "fas fa-users",
        "accounts.usuario": "fas fa-user",
        "products": "fas fa-boxes",
        "products.categoria": "fas fa-tags",
        "products.produto": "fas fa-tshirt",
        "cart": "fas fa-shopping-cart",
        "cart.itemcarrinho": "fas fa-shopping-basket",
        "orders": "fas fa-receipt",
        "auth": "fas fa-user-shield",
        "auth.group": "fas fa-users-cog",
    },

    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
}


# ==========================================================
# CONFIGURAÇÕES GERAIS
# ==========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"