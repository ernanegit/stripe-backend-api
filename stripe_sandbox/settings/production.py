from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    '.railway.app',
    '.vercel.app',
    'localhost',
    '127.0.0.1',
]

# Usar SQLite primeiro para o deploy funcionar
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS para produção
CORS_ALLOWED_ORIGINS = [
    os.getenv('FRONTEND_URL', 'https://your-app.vercel.app'),
]


# CSRF e Origins para Railway
CSRF_TRUSTED_ORIGINS = [
    'https://stripe-backend-api-production.up.railway.app',
    'https://*.railway.app',
]

# Certifique-se de que está nos ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'stripe-backend-api-production.up.railway.app',
    '*.railway.app',
    'localhost',
    '127.0.0.1',
]

# Configurações CSRF para produção
CSRF_COOKIE_SECURE = False  # Temporário para teste
SESSION_COOKIE_SECURE = False  # Temporário para teste




# Desabilitar HTTPS temporariamente 
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
