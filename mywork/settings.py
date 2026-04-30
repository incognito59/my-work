import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-i@yrga*53o@x%tdm8ps)=_zt@obzs4^bx^y)em+r%5)-velltj'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'products.apps.ProductsConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.github',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'mywork.urls'

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

WSGI_APPLICATION = 'mywork.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/products/'
LOGOUT_REDIRECT_URL = '/products/'

# ============ ALLAUTH SETTINGS ============
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'products.adapters.NoSignupFormAdapter'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '774139839237-3e62lmii9cvo2ju690b5hsb79cksol4e.apps.googleusercontent.com',
            'secret': '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',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'consent select_account',
        },
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'VERSION': 'v17.0',
    },
    'github': {
        'APP': {
            'client_id': 'Ov23liSP3Xh0LGviobxc',
            'secret': 'f7751b467a3db033c2e40db25d947d48fc35737d',
        },
        'SCOPE': ['user', 'user:email'],
    },
}

# Firebase project ID for token verification
FIREBASE_PROJECT_ID = 'redcart-d792b'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'afolabiprosper329@gmail.com'
SERVER_EMAIL = 'afolabiprosper329@gmail.com'

# Stripe (keep for later)
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# Paystack
PAYSTACK_PUBLIC_KEY = 'pk_test_4dc9ad4b7bac517bcfd33fb8398a1c3b865e6a2d'
PAYSTACK_SECRET_KEY = 'sk_test_d34aee0fbe64455129b2062c4dcdbd4e87018b64'

# ============ NOTIFICATION SYSTEM SETTINGS ============

# WebSocket/Channels for real-time notifications
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Push Notification VAPID Keys (Generate these for production)
# Run: python -c "from django.core.management import utils; print(utils.get_random_secret_key())"
VAPID_PUBLIC_KEY = 'your-vapid-public-key-here'
VAPID_PRIVATE_KEY = 'your-vapid-private-key-here'
VAPID_EMAIL = 'afolabiprosper329@gmail.com'

# Notification Settings
NOTIFICATION_DEFAULT_DURATION = 5000  # milliseconds
NOTIFICATION_MAX_PER_USER = 100  # Max notifications stored per user
NOTIFICATION_CLEANUP_DAYS = 30  # Delete notifications older than 30 days

# Sound notification files (add these to your static files)
NOTIFICATION_SOUNDS = {
    'default': '/static/sounds/notification.mp3',
    'success': '/static/sounds/success.mp3',
    'error': '/static/sounds/error.mp3',
    'warning': '/static/sounds/warning.mp3',
    'order': '/static/sounds/order.mp3',
}

# Email notification settings
EMAIL_NOTIFICATION_ENABLED = True
EMAIL_NOTIFICATION_BATCH_SIZE = 50

# Real-time settings
REAL_TIME_NOTIFICATIONS_ENABLED = True

# System Alert Checks (in seconds)
SYSTEM_ALERT_CHECK_INTERVAL = 300  # 5 minutes
LOW_STOCK_THRESHOLD = 5
ABANDONED_CART_HOURS = 24

# Cache settings for notifications
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

SITE_ID = 1
ITEMS_PER_PAGE = 12
CURRENCY = 'NGN'
CURRENCY_SYMBOL = '₦'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'frontend']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'