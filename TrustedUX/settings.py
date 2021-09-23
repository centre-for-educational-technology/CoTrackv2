"""
Django settings for TrustedUX project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _



ETHERPAD_KEY = "19a6d96ea14df62331708d6e68cf043267c6e4a96ce177bac6d34bb94db19c9d"
ETHERPAD_URL ="https://www.etherpad.website"

JW_SEC = "PANKAJBFA26C645791DFF128F3EF1251798F0E"
JW_APP = "62DD4"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

PROTOCOL = 'https'
SESSION_COOKIE_SECURE = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CKeditor settings
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_RESTRICT_BY_USER = True
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0abn2aukso9r5!7zuk$tk7q%0%=$jxuocgfm%pu_lsgq!$+*e+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.cotrack.website']

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#EMAIL_BACKEND = 'django_mailjet.backends.MailjetBackend'
MAILJET_API_KEY = '39b93cd219afa7bbfda355795fcf7b94'
MAILJET_API_SECRET = 'f29eb65e1b46c83c577075c93612ba51'


LOGIN_URL = '/login/'

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True
LOGIN_REDIRECT_URL = "/enter"

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "crispy_forms",
    "register",
    'ckeditor',
    'ckeditor_uploader',
    "esurvey",
    "formtools",
    "djrichtextfield",
    'django.contrib.sites',
    'rest_framework',
    'django_toggle_switch_widget',
    'django_extensions',


    'allauth',   # <--
    'allauth.account',   # <--
    'allauth.socialaccount',   # <--
    'allauth.socialaccount.providers.google',   # <--
    'allauth.socialaccount.providers.facebook',


]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

CRISPY_TEMPLATE_PACK = "bootstrap4"

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TrustedUX.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates'),os.path.join(BASE_DIR,'register','templates'),os.path.join(BASE_DIR,'esurvey','templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request'
            ],
            'libraries':{
                'my_tags': 'esurvey.templatetags.my_tags',

            }
        },
    },
]


WSGI_APPLICATION = 'TrustedUX.wsgi.application'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook':
       {'METHOD': 'oauth2',
        'SCOPE': ['email','public_profile', 'user_friends'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'kr_KR',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.4'}
}

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cotrack_db',
        'USER': 'etherpad',
        'PASSWORD': 'phanu',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

"""

DJRICHTEXTFIELD_CONFIG = {
    'js': ["//cdnjs.cloudflare.com/ajax/libs/tinymce/5.6.1/tinymce.min.js"],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': True,
        'plugins': 'link image lists advlist table',
        'toolbar': 'bold italic underline | link image table | fontselect fontsizeselect | alignleft aligncenter alignright alignjustify | numlist bullist  | removeformat',

    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-gb'

LAGUAGES = (('en',_('English')),('ee',_('Estonian')),('pt',_('Portugese')))


TIME_ZONE =  'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
    'image_previewText': '',
        #'skin': 'moono',
        'skil': 'bootstrapck',
        #'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'VideoDetector', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},

            '/',  # put this to force next toolbar on new line

        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
         'width': '100%',
         'image_previewText': '',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'uploadfile',
            'videodetector',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}



STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = os.path.join(SETTINGS_PATH, '/static/')
ASGI_APPLICATION = 'esurvey.asgi.application'
