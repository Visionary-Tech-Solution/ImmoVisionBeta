"""
Django settings for immovision project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Install Apps 
    'authentication.apps.AuthenticationConfig',
    'account.apps.AccountConfig',
    'common.apps.CommonConfig',
    'order.apps.OrderConfig',
    'upload_video.apps.UploadVideoConfig',
    'recovery_account',
    'notifications',

    # Install Third Party
    'rest_framework',
    "phonenumber_field",
    "corsheaders",
    'drf_yasg'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'immovision.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

WSGI_APPLICATION = 'immovision.wsgi.application'
AUTH_USER_MODEL = 'authentication.User'
CORS_ALLOW_ALL_ORIGINS=True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'immovision',
        'USER': 'immovisionuser',
        'PASSWORD': 'immovision_vts',
        'HOST': 'realvisionmedia-prod-rds-postgre.ck6l4girjtar.us-east-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = []
MEDIA_ROOT = 'media/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'






# #mail sending purpose
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'#oke
# EMAIL_HOST = 'smtp.gmail.com'#oke

# EMAIL_PORT = '587'#oke
# EMAIL_HOST_USER = 'lawyertrive@gmail.com'#leave here your genuine email
# #EMAIL_HOST_PASSWORD = 'zqrgvttkmlpxuqjy'#leave here your genuine password of your email. keep it in mind, as the password should in encrypted condition 
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = True#oke
# #oke
#STRIPE_PUBLISHABLE_KEY = 'pk_test_51NDCcNE93DJrdmX9hXS3d0gF0f8NIeGMWUKvsrdgbDdqRg4uNfdMmhj2tLl3g4kA3cMsKxjPAe4hDTOtVZbyVAtm00dYSa9ZQt'
#STRIPE_SECRET_KEY = 'sk_test_51NDCcNE93DJrdmX9SATxuuX0vVgoSlrsuH9DQ4GIs0NUbBGRY6letDGF8DtOBdByu5VS0Xcr3o0BCYSs9GfGuJ2Z00GJ3VE1JZ'

STRIPE_SECRET_KEY = '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'
STRIPE_PUBLISHABLE_KEY = 'pk_live_51NDCcNE93DJrdmX9LtRTIduTA08PNd8cHejw2oCyMVydod534uBx4J8Gk8KwFV7jyjPhqqT1vNG8lyal9IN2J97800HrUwNR7k'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@realvisionmedia.com'
EMAIL_HOST_PASSWORD = 'avqmnleqwducnido'
EMAIL_USE_TLS = True



# wuth custom email
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'#oke
# EMAIL_HOST = 'mail.rvk.in'
# EMAIL_PORT = '465'#oke
# EMAIL_HOST_USER = 'donotreply@rvk.in'#leave here your genuine email
# EMAIL_HOST_PASSWORD = 'Tpy@475631'#leave here your genuine password of your email. keep it in mind, as the password should in encrypted condition 
# EMAIL_USE_SSL = True#oke
 
