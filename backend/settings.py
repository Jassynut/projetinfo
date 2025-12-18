"""
Django settings for projetinfo project - VERSION DOCKER COMPATIBLE
"""

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-w2(c2(oo-ad&=878nqa2)5f884t^4jj&je^-4rw+503l4-9p!f')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS pour Docker
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,10.24.159.13,*')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

# Ajouter les noms des services Docker
ALLOWED_HOSTS.extend(['db', 'backend', 'frontend'])

sys.path.insert(0, os.path.join(BASE_DIR))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'hse_app',
    'certificats',
    'stats',
    'tests',
    'authentication',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database configuration pour Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME', 'hse_database'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', 'root'),
        'HOST': os.getenv('DATABASE_HOST', 'db'),  # 'db' = nom du service dans Docker
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
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

AUTHENTICATION_BACKENDS = [
    'authentication.backend.AdminBackend',
    'authentication.backend.HSEUserBackend',
    'authentication.backend.HSEManagerBackend',
]

AUTH_USER_MODEL = 'authentication.TestUser'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = '/app/static'  # IMPORTANT: Doit correspondre au volume Docker
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'  # IMPORTANT: Doit correspondre au volume Docker

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS configuration pour Docker
CORS_ALLOW_CREDENTIALS = True

# FRONTEND_URL depuis les variables d'environnement
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://10.24.159.13:3000')

# URLs dynamiques basées sur FRONTEND_URL
frontend_origin = FRONTEND_URL.rstrip('/')
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:80",  # Frontend dans Docker sur port 80
    "http://frontend:80",   # Frontend service dans Docker
    "http://10.24.159.13:3000",  # IP locale frontend
    frontend_origin,        # Ton URL frontend
]

# Ajouter aussi le backend lui-même
CORS_ALLOWED_ORIGINS.extend([
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://backend:8000",  # Backend service dans Docker
    "http://10.24.159.13:8000",  # IP locale backend
])

# Pour le développement, tu peux autoriser toutes les origines
# CORS_ALLOW_ALL_ORIGINS = True  # À décommenter si tu as des problèmes
# Note: Actuellement désactivé car on utilise une liste explicite

# Configuration des cookies pour Docker
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # True si tu utilises HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24h
SESSION_COOKIE_DOMAIN = None  # Important pour Docker

CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False  # Doit être False pour que JS puisse lire
CSRF_COOKIE_DOMAIN = None

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:80",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://backend:8000",
    "http://10.24.159.13:3000",
    "http://10.24.159.24:3000",  # Nouvelle IP frontend
    "http://10.24.159.13:8000",
    frontend_origin,
]

# Pour le développement, autoriser toutes les origines si nécessaire
# CORS_ALLOW_ALL_ORIGINS = True  # Décommenter en cas de problème CORS

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# URLs de login/logout
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/stats/'
LOGOUT_REDIRECT_URL = '/'

# Logging pour Docker
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
}