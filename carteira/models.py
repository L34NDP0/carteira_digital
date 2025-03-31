from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

# Modelo que representa a carteira de um usuário
class Carteira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    saldo = models.DecimalField(
        max_digits=10,  # Suporta valores grandes, até 99999999.99
        decimal_places=2,  # Apenas duas casas decimais, adequado para valores monetários
        default=0,  # Saldo inicial da carteira é 0
        validators=[MinValueValidator(Decimal('0.00'))]  # Garante que o saldo nunca seja negativo
    )
    criado_em = models.DateTimeField(auto_now_add=True) # Registra automaticamente a data de criação da carteira
    atualizado_em = models.DateTimeField(auto_now=True) # Atualiza automaticamente a data sempre que a carteira for atualizada
    
    def __str__(self):
        return f"Carteira de {self.usuario.username}"

# Bloco que representa uma transação entre usuários
class Transacao(models.Model):
    TIPOS_TRANSACAO = (
        ('DEPOSITO', 'Depósito'),  # Quando um usuário adiciona dinheiro à sua carteira
        ('TRANSFERENCIA', 'Transferência'),  # Quando um usuário transfere dinheiro para outro usuário
    )
    # Remetente
    remetente = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Protege a integridade dos dados impedindo exclusão de usuários com transações associadas
        related_name='transacoes_enviadas'  # Permite acessar as transações enviadas por um usuário
    )
    # Destinatário
    destinatario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Impede exclusão de usuários com transações associadas
        related_name='transacoes_recebidas'  # Permite acessar as transações recebidas por um usuário
    )
    # Valor
    valor = models.DecimalField(
        max_digits=10,  
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]  # Garante que transações tenham valor mínimo de R$ 0,01
    )
    # Define o tipo da transação
    tipo_transacao = models.CharField(
        max_length=15,
        choices=TIPOS_TRANSACAO
    )

    realizado_em = models.DateTimeField(auto_now_add=True) # Registra automaticamente a data e hora da transação

    def __str__(self):
        return f"{self.tipo_transacao} - {self.remetente.username} para {self.destinatario.username}: R${self.valor}"
