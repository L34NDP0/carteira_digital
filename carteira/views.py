from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Carteira, Transacao
from .serializers import (
    UsuarioSerializer,
    CarteiraSerializer,
    TransacaoSerializer,
    TransferenciaSerializer,
    DepositoSerializer
)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']


class CarteiraViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarteiraSerializer

    def get_queryset(self):
        return Carteira.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def deposito(self, request):
        serializer = DepositoSerializer(data=request.data)
        if serializer.is_valid():
            valor = serializer.validated_data['valor']
            
            with transaction.atomic():
                carteira = Carteira.objects.select_for_update().get(usuario=request.user)
                carteira.saldo += valor
                carteira.save()

                Transacao.objects.create(
                    remetente=request.user,
                    destinatario=request.user,
                    valor=valor,
                    tipo_transacao='DEPOSITO'
                )

            return Response({'mensagem': 'Depósito realizado com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def transferencia(self, request):
        serializer = TransferenciaSerializer(data=request.data)
        if serializer.is_valid():
            valor = serializer.validated_data['valor']
            destinatario_username = serializer.validated_data['destinatario_username']

            try:
                destinatario = User.objects.get(username=destinatario_username)
            except User.DoesNotExist:
                return Response(
                    {'erro': 'Usuário destinatário não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if destinatario == request.user:
                return Response(
                    {'erro': 'Não é possível transferir para si mesmo'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                remetente_carteira = Carteira.objects.select_for_update().get(
                    usuario=request.user)
                destinatario_carteira = Carteira.objects.select_for_update().get(
                    usuario=destinatario)

                if remetente_carteira.saldo < valor:
                    return Response(
                        {'erro': 'Saldo insuficiente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                remetente_carteira.saldo -= valor
                destinatario_carteira.saldo += valor
                
                remetente_carteira.save()
                destinatario_carteira.save()

                Transacao.objects.create(
                    remetente=request.user,
                    destinatario=destinatario,
                    valor=valor,
                    tipo_transacao='TRANSFERENCIA'
                )

            return Response({'mensagem': 'Transferência realizada com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransacaoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransacaoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'criado_em': ['gte', 'lte'],
    }

    def get_queryset(self):
        return Transacao.objects.filter(
            remetente=self.request.user
        ).order_by('-criado_em')

