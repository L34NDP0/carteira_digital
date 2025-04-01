from .settings import *

# Usa o SQLite em memória para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desabilitado o debug para testes
DEBUG = False

# Chave secreta fixa para testes
SECRET_KEY = 'test-key-not-for-production'

# Permitir todos os hosts em testes
ALLOWED_HOSTS = ['*']