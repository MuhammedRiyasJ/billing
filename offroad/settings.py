import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'x3ca%=v)_oi^8$#fc%5#smdwym9_^7y$pl2m=f&s+xi)*eit#f'

DEBUG = True

STATIC_ROOT = '/home/hardline/webapps/django_offroad_static'

ALLOWED_HOSTS = []


INSTALLED_APPS = [
 
    'dal',
    'dal_select2',
    'pytz',
    'xlsxwriter',
    'keyboard_shortcuts',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app',
    'shops',
    'users',
    'products',
    'vendors',
    'customers',
    'purchases',
    'sales',  
    'expense', 
    'cheques', 

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'offroad.middleware.middleware.cheque_notification_middleware'
]

ROOT_URLCONF = 'offroad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.main_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'offroad.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'offroad',  
        'USER': 'offroad',
        'PASSWORD': 'offroad',
        'HOST': 'localhost',             
        'PORT': '',                    
    }
}



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

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

DATETIME_INPUT_FORMATS = ['%d-%m-%Y']

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = False

USE_TZ = False


# START keyboard_shortcuts settings #
HOTKEYS = [
            {'keys': 'ctrl + d + a',  # go home
            'link': '/'},
            {'keys': 'ctrl + s + a',  # go Create Sale
            'link': '/sales/create-sale'},
            {'keys': 'ctrl + p + u',  # go Create Purchase
            'link': '/purchases/create-purchase'},
            {'keys': 'ctrl + p + r ',  # go Create Product
            'link': '/products/create-product'},
            {'keys': 'ctrl + c + u',  # go Create Customer
            'link': '/customers/create-customer'},
            {'keys': 'ctrl + v + e',  # go Create Vendor
            'link': '/vendors/create-vendor'},
            {'keys': 'ctrl + e + x',  # go Create Expense
            'link': '/expense/create-expense/'},
            {'keys': 'ctrl + c + h',  # go Create Cheque Details
            'link': '/cheque-details/create-cheque-details/'},
        ]

SPECIAL_DISABLED = True
# END keyboard_shortcuts settings #


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = '/static/'
STATIC_FILE_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
