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

# Desabilitar HTTPS temporariamente 
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True