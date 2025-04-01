from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, CarteiraViewSet, TransacaoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario') #Criação de usuários
router.register(r'carteiras', CarteiraViewSet, basename='carteira') #Gerenciamento de carteiras
router.register(r'transacoes', TransacaoViewSet, basename='transacao') #Histórico de transações

urlpatterns = [
    path('', include(router.urls)),
]

