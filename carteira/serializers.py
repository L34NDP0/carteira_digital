from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Carteira, Transacao

# Função para criação e gerenciamento de usuários
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Senha nunca é exposta nas respostas da API
    criado_em = serializers.DateTimeField(source='date_joined', read_only=True)  # data criação

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'criado_em')

    def create(self, validated_data):
        """Criação de usuário com senha hash e carteira automática"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        Carteira.objects.create(usuario=user)  # Ao criar um usuário, cria-se automaticamente uma carteira associada
        return user

# Função para exibição do saldo da carteira
class CarteiraSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)  # Inclui o nome do usuário na resposta

    class Meta:
        model = Carteira
        fields = ('id', 'username', 'saldo', 'criado_em', 'atualizado_em')
        read_only_fields = ('saldo',)  # Garante que o saldo não pode ser alterado via API

# Função para exibição de transações
class TransacaoSerializer(serializers.ModelSerializer):
    remetente_username = serializers.CharField(source='remetente.username', read_only=True)
    destinatario_username = serializers.CharField(source='destinatario.username', read_only=True)
    data = serializers.DateTimeField(source='realizado_em', format='%Y-%m-%d', read_only=True)  # Formata data e hora separadamente
    hora = serializers.DateTimeField(source='realizado_em', format='%H:%M:%S', read_only=True)  

    class Meta:
        model = Transacao
        fields = ('id', 'remetente_username', 'destinatario_username', 'valor',
                  'tipo_transacao', 'data', 'hora')
        read_only_fields = ('remetente', 'tipo_transacao')  # Remetente e tipo não podem ser modificados via API

# Função para validar dados de transferência
class TransferenciaSerializer(serializers.Serializer):
    destinatario_username = serializers.CharField()  # Nome do usuário destinatário
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)  # Valor a ser transferido

    def validate_valor(self, value):
        """Garante que o valor da transferência seja positivo"""
        if value <= 0:
            raise serializers.ValidationError("O valor da transferência deve ser maior que zero")
        return value

# Função para validar depósitos
class DepositoSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)  # Valor a ser depositado

    def validate_valor(self, value):
        """Garante que o valor do depósito seja positivo"""
        if value <= 0:
            raise serializers.ValidationError("O valor do depósito deve ser maior que zero")
        return value
