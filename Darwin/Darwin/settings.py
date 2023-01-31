"""
Django settings for Darwin project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-003oo_(urn&%(5*-1i**_mlipq5se_p7uy7x7$8uaxapz1*s#o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apis',     #apis app

    #3rd party
    'rest_framework',
    'corsheaders',
]

#cors config
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://localhost:3000',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',    #cors
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #user defined middleware
    'apis.middleware.AuthenticateMiddleware'
]

ROOT_URLCONF = 'Darwin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Darwin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#mongo_auth db settings
MANGO_JWT_SETTINGS = {
    "db_host": "localhost", # Use srv host if connecting with MongoDB Atlas Cluster
    "db_port": "27017", # Don't include this field if connecting with MongoDB Atlas Cluster
    "db_name": "mystore",
    "db_user": "username",
    "db_pass": "password",
    "auth_collection": "User",
    "fields": ("email", "password"), # default
    "jwt_secret": "secret", # default
    "jwt_life": 2, # default (in hours)
    # "secondary_username_field": "mobile_no" # default is None
}



#firebase product-image-upload configs

FIREBASECONFIG = {
#   "apiKey": "AIzaSyA3PdpsewMS99e-_S_SzqrWvSGYHx2rnAs",
#   "authDomain": "online-store-37.firebaseapp.com",
#   "projectId": "online-store-37",
#   "storageBucket": "online-store-37.appspot.com",
# #   "appId": "1:60952080625:web:12497213ce9fe2d927f950",
#   "databaseURL": "https://online-store-37-default-rtdb.firebaseio.com",
            "apiKey": "AIzaSyBSZIUFp4dkPZqVHCGGph0RTb_Bq9cgH7Q",
          "authDomain": "clothing-store-2.firebaseapp.com",
          "projectId": "clothing-store-2",
          "storageBucket": "clothing-store-2.appspot.com",
          "messagingSenderId": "849818401432",
          "appId": "1:849818401432:web:b3c51287604d037f552eed",
          "measurementId": "G-P18RPNLV1X",
  "databaseURL": "https://clothing-store-2-default-rtdb.firebaseio.com/",
}

MAIL_SERVICE_CONFIGS = {
    'sender' : 'gurukrupafashion90@gmail.com',
    'password': 'odniwlwizogvkgch',
    'smtp_server' : 'smtp.gmail.com',
    'smtp_port': 465
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'


##### added for firebase image upload
# Actual directory user files go to
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'mediafiles')

# URL used to access the media
MEDIA_URL = '/media/'


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
