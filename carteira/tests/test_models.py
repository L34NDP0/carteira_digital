from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from carteira.models import Carteira, Transacao


class CarteiraModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)

    def test_criar_carteira_com_saldo_inicial_zero(self):
        """Teste se a carteira é criada com saldo zero"""
        self.assertEqual(self.carteira.saldo, Decimal('0.00'))

    def test_string_representation(self):
        """Teste a representação string do modelo"""
        self.assertEqual(str(self.carteira), f"Carteira de {self.user.username}")

    def test_saldo_negativo_nao_permitido(self):
        """Teste se não é possível ter saldo negativo"""
        self.carteira.saldo = Decimal('-1.00')
        with self.assertRaises(ValidationError):
            self.carteira.full_clean()

    def test_saldo_maximo_permitido(self):
        """Teste se o saldo máximo está dentro do limite permitido"""
        self.carteira.saldo = Decimal('9999999.99')
        try:
            self.carteira.full_clean()
        except ValidationError:
            self.fail("Não deveria levantar ValidationError")


class TransacaoModelTest(TestCase):
    def setUp(self):
        self.remetente = User.objects.create_user(
            username='remetente',
            password='testpass123'
        )
        self.destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )

    def test_criar_transacao_deposito(self):
        """Teste criar uma transação de depósito"""
        transacao = Transacao.objects.create(
            remetente=self.remetente,
            destinatario=self.remetente,
            valor=Decimal('100.00'),
            tipo_transacao='DEPOSITO'
        )
        self.assertEqual(transacao.valor, Decimal('100.00'))
        self.assertEqual(transacao.tipo_transacao, 'DEPOSITO')

    def test_criar_transacao_transferencia(self):
        """Teste criar uma transação de transferência"""
        transacao = Transacao.objects.create(
            remetente=self.remetente,
            destinatario=self.destinatario,
            valor=Decimal('50.00'),
            tipo_transacao='TRANSFERENCIA'
        )
        self.assertEqual(transacao.valor, Decimal('50.00'))
        self.assertEqual(transacao.tipo_transacao, 'TRANSFERENCIA')

    def test_valor_minimo_transacao(self):
        """Teste se não é possível criar transação com valor menor que 0.01"""
        with self.assertRaises(ValidationError):
            transacao = Transacao(
                remetente=self.remetente,
                destinatario=self.destinatario,
                valor=Decimal('0.00'),
                tipo_transacao='TRANSFERENCIA'
            )
            transacao.full_clean()