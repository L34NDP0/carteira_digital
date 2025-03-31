from .settings import *

# Usar SQLite em memória para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desabilitar debug para testes
DEBUG = False

# Chave secreta fixa para testes
SECRET_KEY = 'test-key-not-for-production'

# Permitir todos os hosts em testes
ALLOWED_HOSTS = ['*']