from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Carteira, Transacao


class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'senha')

    def create(self, validated_data):
        usuario = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['senha']
        )
        Carteira.objects.create(usuario=usuario)
        return usuario


class CarteiraSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Carteira
        fields = ('id', 'username', 'saldo', 'criado_em', 'atualizado_em')
        read_only_fields = ('saldo',)


class TransacaoSerializer(serializers.ModelSerializer):
    remetente_username = serializers.CharField(source='remetente.username', read_only=True)
    destinatario_username = serializers.CharField(source='destinatario.username', read_only=True)

    class Meta:
        model = Transacao
        fields = ('id', 'remetente_username', 'destinatario_username', 'valor',
                 'tipo_transacao', 'criado_em')
        read_only_fields = ('remetente', 'tipo_transacao')


class TransferenciaSerializer(serializers.Serializer):
    destinatario_username = serializers.CharField()
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "O valor da transferência deve ser maior que zero")
        return value


class DepositoSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "O valor do depósito deve ser maior que zero")
        return value
