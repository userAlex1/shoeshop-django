"""
Django settings for shoeshop project.
"""
import os
from pathlib import Path
from decouple import config
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core ---
SECRET_KEY = config('SECRET_KEY', default='dev-only-secret-key-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = [
    "shoeshop-19i2kq7m8-useralex1s-projects.vercel.app",
    "shoeshop-tau-five.vercel.app",
    "localhost",
    "127.0.0.1",
]
#ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'store',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shoeshop.urls'

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
                'store.context_processors.cart_summary',
            ],
        },
    },
]

WSGI_APPLICATION = 'shoeshop.wsgi.application'

# --- Database ---
# Defaults to SQLite for easy local dev. Swap to Postgres in production
# by setting DATABASE_URL and using dj-database-url (see README).
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'store:home'
LOGOUT_REDIRECT_URL = 'store:login'
LOGIN_URL = 'store:login'

# =========================================================
# M-PESA DARAJA SETTINGS (Safaricom)
# Get sandbox credentials at https://developer.safaricom.co.ke
# =========================================================
MPESA_ENV = config('MPESA_ENV', default='sandbox')  # 'sandbox' or 'production'
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='174379')  # sandbox default test shortcode
MPESA_PASSKEY = config('MPESA_PASSKEY', default='')
# Must be a PUBLIC https URL Safaricom can reach (use ngrok in dev)
MPESA_CALLBACK_URL = config('MPESA_CALLBACK_URL', default='MPESA_CALLBACK_URL=https://finance-expenses-maturing.ngrok-free.dev/payments/mpesa/callback/')

# =========================================================
# PAYSTACK SETTINGS (cards / bank transfer)
# Get keys at https://dashboard.paystack.com/#/settings/developer
# =========================================================
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
