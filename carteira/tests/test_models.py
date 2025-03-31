from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from carteira.models import Carteira, Transacao


# Testes para o modelo Carteira
class CarteiraModelTest(TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)

    def test_criar_carteira_com_saldo_inicial_zero(self):
        """Teste se a carteira é criada com saldo inicial de 0.00"""
        self.assertEqual(self.carteira.saldo, Decimal('0.00'))

    def test_string_representation(self):
        """Teste a representação em string do modelo Carteira"""
        self.assertEqual(str(self.carteira), f"Carteira de {self.user.username}")

    def test_saldo_negativo_nao_permitido(self):
        """Teste se não é possível ter saldo negativo na carteira"""
        self.carteira.saldo = Decimal('-1.00')
        
        # full_clean() deve levantar ValidationError se o saldo for negativo
        with self.assertRaises(ValidationError):
            self.carteira.full_clean()

    def test_saldo_maximo_permitido(self):
        """Teste se um saldo alto dentro do limite permitido não gera erro"""
        self.carteira.saldo = Decimal('9999999.99')
        
        # O teste deve passar sem levantar um erro
        try:
            self.carteira.full_clean()
        except ValidationError:
            self.fail("Não deveria levantar ValidationError para saldo dentro do limite permitido")


# Testes para o modelo Transacao
class TransacaoModelTest(TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
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
            remetente=self.remetente,  # No caso de depósito, remetente e destinatário são o mesmo usuário
            destinatario=self.remetente,
            valor=Decimal('100.00'),
            tipo_transacao='DEPOSITO'
        )
        
        # Verifica se os valores foram corretamente armazenados no banco de dados
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
        
        # Verifica se os valores foram corretamente armazenados
        self.assertEqual(transacao.valor, Decimal('50.00'))
        self.assertEqual(transacao.tipo_transacao, 'TRANSFERENCIA')

    def test_valor_minimo_transacao(self):
        """Teste se não é possível criar transação com valor menor que 0.01"""
        with self.assertRaises(ValidationError):
            transacao = Transacao(
                remetente=self.remetente,
                destinatario=self.destinatario,
                valor=Decimal('0.00'),  # Valor inválido
                tipo_transacao='TRANSFERENCIA'
            )
            transacao.full_clean()  # Deve levantar ValidationError
