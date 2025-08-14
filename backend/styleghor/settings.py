from pathlib import Path
import os

# ----------------------------
# Base Directory
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# SECURITY
# ----------------------------
SECRET_KEY = 'django-insecure-your-secret-key'  # Change in production
DEBUG = True
ALLOWED_HOSTS = ['*']  # Update with your domain in production

# ----------------------------
# Site Configuration
# ----------------------------
SITE_URL = 'http://localhost:8000'  # Update with your domain in production
SITE_NAME = 'Style Ghor'
SITE_DESCRIPTION = 'Your Fashion Destination'

# ----------------------------
# Installed Apps
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',             # Your store app
    'users',            # Your custom users app
    'rest_framework',   # API support
    'corsheaders',      # Frontend CORS
]

# ----------------------------
# Authentication
# ----------------------------
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/users/login/'

# ----------------------------
# Templates
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ----------------------------
# Middleware
# ----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----------------------------
# CORS
# ----------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Frontend dev
    "http://localhost:8000",  # Django dev
]

# ----------------------------
# URLs & WSGI
# ----------------------------
ROOT_URLCONF = 'styleghor.urls'

WSGI_APPLICATION = 'styleghor.wsgi.application'

# ----------------------------
# Database
# ----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Change to PostgreSQL in production
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ----------------------------
# Password Validation
# ----------------------------
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

# ----------------------------
# Internationalization
# ----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# ----------------------------
# Static & Media
# ----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Additional static files directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ----------------------------
# Default primary key field type
# ----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------
# SSLCommerz Payment Settings
# ----------------------------
SSL_COMMERZ_STORE_ID = "your_test_store_id"
SSL_COMMERZ_STORE_PASSWORD = "your_test_store_password"
SSL_COMMERZ_SANDBOX = True  # True = Sandbox, False = Live

# ----------------------------
# REST Framework (optional, for API)
# ----------------------------
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# ----------------------------
# Email Configuration
# ----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Change in production
DEFAULT_FROM_EMAIL = 'noreply@styleghor.com'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

# ----------------------------
# Session Configuration
# ----------------------------
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# ----------------------------
# Message Framework
# ----------------------------
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# ----------------------------
# Security Settings (for production)
# ----------------------------
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
