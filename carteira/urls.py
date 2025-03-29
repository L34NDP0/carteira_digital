from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, CarteiraViewSet, TransacaoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'carteiras', CarteiraViewSet, basename='carteira')
router.register(r'transacoes', TransacaoViewSet, basename='transacao')

urlpatterns = [
    path('', include(router.urls)),
]
