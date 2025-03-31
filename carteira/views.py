from rest_framework import viewsets, status
from django_filters import rest_framework as filters
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

# Função responsável pelo cadastro de usuários
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]  # Permite acesso público (qualquer um pode criar um usuário, pode ser alterado)
    http_method_names = ['post']  # Restringe a API para permitir apenas a criação de usuários (POST)

# Função responsável por exibir o saldo da carteira e realizar transações
class CarteiraViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarteiraSerializer

    # Retorna apenas a carteira do usuário autenticado
    def get_queryset(self):
        return Carteira.objects.filter(usuario=self.request.user)

    # Endpoint para depósito de dinheiro na carteira
    @action(detail=False, methods=['post'])
    def deposito(self, request):
        serializer = DepositoSerializer(data=request.data)
        if serializer.is_valid():
            valor = serializer.validated_data['valor']

            # Utiliza uma transação atômica para garantir consistência dos dados
            with transaction.atomic():
                carteira = Carteira.objects.select_for_update().get(usuario=request.user)
                carteira.saldo += valor
                carteira.save()

                # Registra a transação de depósito
                Transacao.objects.create(
                    remetente=request.user,
                    destinatario=request.user,  # No caso de depósito, remetente e destinatário são o próprio usuário
                    valor=valor,
                    tipo_transacao='DEPOSITO'
                )

            return Response({'mensagem': 'Depósito realizado com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Endpoint para transferências entre usuários
    @action(detail=False, methods=['post'])
    def transferencia(self, request):
        serializer = TransferenciaSerializer(data=request.data)
        if serializer.is_valid():
            valor = serializer.validated_data['valor']
            destinatario_username = serializer.validated_data['destinatario_username']

            # Verifica se o destinatário existe
            try:
                destinatario = User.objects.get(username=destinatario_username)
            except User.DoesNotExist:
                return Response(
                    {'erro': 'Usuário destinatário não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Impede transferências para si mesmo
            if destinatario == request.user:
                return Response(
                    {'erro': 'Não é possível transferir para si mesmo'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Transação atômica para garantir consistência dos saldos
            with transaction.atomic():
                remetente_carteira = Carteira.objects.select_for_update().get(usuario=request.user)
                destinatario_carteira = Carteira.objects.select_for_update().get(usuario=destinatario)

                # Verifica se há saldo suficiente
                if remetente_carteira.saldo < valor:
                    return Response(
                        {'erro': 'Saldo insuficiente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Lógica que deduz o valor do saldo do remetente e adiciona ao saldo do destinatário
                remetente_carteira.saldo -= valor
                destinatario_carteira.saldo += valor

                remetente_carteira.save()
                destinatario_carteira.save()

                # Registra a transação de transferência
                Transacao.objects.create(
                    remetente=request.user,
                    destinatario=destinatario,
                    valor=valor,
                    tipo_transacao='TRANSFERENCIA'
                )

            return Response({'mensagem': 'Transferência realizada com sucesso'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Filtro para consultas de transações por data e tipo
class TransacaoFilter(filters.FilterSet):
    data_inicio = filters.DateTimeFilter(field_name='realizado_em', lookup_expr='gte')
    data_fim = filters.DateTimeFilter(field_name='realizado_em', lookup_expr='lte')
    tipo = filters.ChoiceFilter(field_name='tipo_transacao', choices=Transacao.TIPOS_TRANSACAO)

    class Meta:
        model = Transacao
        fields = ['tipo_transacao', 'realizado_em']

# Função para exibição de transações
class TransacaoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransacaoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransacaoFilter
    ordering_fields = ['realizado_em', 'valor']
    ordering = ['-realizado_em']  # Ordenação padrão, mais recente primeiro

    # Função que retorna apenas as transações feitas pelo usuário autenticado
    def get_queryset(self):
        return Transacao.objects.filter(
            remetente=self.request.user
        ).order_by('-realizado_em')
