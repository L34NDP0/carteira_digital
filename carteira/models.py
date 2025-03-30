from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Carteira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carteira de {self.usuario.username}"


class Transacao(models.Model):
    TIPOS_TRANSACAO = (
        ('DEPOSITO', 'Depósito'),
        ('TRANSFERENCIA', 'Transferência'),
    )

    remetente = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transacoes_enviadas'
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='transacoes_recebidas'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tipo_transacao = models.CharField(
        max_length=15,
        choices=TIPOS_TRANSACAO
    )
    realizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_transacao} - {self.remetente} para {self.destinatario}: R${self.valor}"
