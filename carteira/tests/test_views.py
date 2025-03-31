from django.test import TransactionTestCase
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from carteira.models import Carteira, Transacao
from rest_framework.test import APIClient


# Testes para criação de usuários
class UsuarioViewSetTest(TransactionTestCase):
    def test_criar_usuario_sucesso(self):
        """Teste criar usuário com sucesso"""
        url = reverse('usuario-list')  # Rota para criação de usuários
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        # Verifica se a resposta foi 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se o usuário foi criado no banco de dados
        self.assertTrue(User.objects.filter(username='testuser').exists())

        # Verifica se uma carteira foi criada automaticamente para o usuário
        self.assertTrue(Carteira.objects.filter(usuario__username='testuser').exists())

    def test_criar_usuario_username_duplicado(self):
        """Teste tentar criar usuário com username já existente"""
        User.objects.create_user(username='testuser', password='testpass123')
        url = reverse('usuario-list')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        # Deve retornar 400 Bad Request, pois o username já existe
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Testes para a Carteira (depósitos e transferências)
class CarteiraViewSetTest(TransactionTestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.api_client = APIClient()

        # Criar um usuário e autenticá-lo
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.api_client.force_authenticate(user=self.user)

    def test_deposito_sucesso(self):
        """Teste realizar depósito com sucesso"""
        url = reverse('carteira-deposito')
        data = {'valor': '100.00'}
        response = self.api_client.post(url, data, format='json')

        # Verifica se a resposta foi 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Atualiza os dados da carteira no banco de dados e verifica se o saldo aumentou
        self.carteira.refresh_from_db()
        self.assertEqual(self.carteira.saldo, Decimal('100.00'))

    def test_deposito_valor_negativo(self):
        """Teste tentar realizar depósito com valor negativo"""
        url = reverse('carteira-deposito')
        data = {'valor': '-100.00'}
        response = self.api_client.post(url, data, format='json')

        # Verifica se a resposta foi 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transferencia_sucesso(self):
        """Teste realizar transferência com sucesso"""
        destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        Carteira.objects.create(usuario=destinatario)

        # Adiciona saldo suficiente para realizar a transferência
        self.carteira.saldo = Decimal('100.00')
        self.carteira.save()

        url = reverse('carteira-transferencia')
        data = {
            'destinatario_username': 'destinatario',
            'valor': '50.00'
        }
        response = self.api_client.post(url, data, format='json')

        # Verifica se a transferência foi realizada com sucesso
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transferencia_saldo_insuficiente(self):
        """Teste tentar transferir com saldo insuficiente"""
        destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        Carteira.objects.create(usuario=destinatario)

        url = reverse('carteira-transferencia')
        data = {
            'destinatario_username': 'destinatario',
            'valor': '100.00'  # Usuário não tem saldo suficiente
        }
        response = self.api_client.post(url, data, format='json')

        # Deve retornar erro 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verifica se a mensagem de erro correta foi retornada
        self.assertEqual(response.data['erro'], 'Saldo insuficiente')


# Testes para a visualização de transações
class TransacaoViewSetTest(TransactionTestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.api_client = APIClient()

        # Criar usuário e carteira
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.api_client.force_authenticate(user=self.user)

    def test_listar_transacoes(self):
        """Teste listar transações do usuário"""
        # Criar algumas transações de exemplo
        Transacao.objects.create(
            remetente=self.user,
            destinatario=self.user,
            valor=Decimal('100.00'),
            tipo_transacao='DEPOSITO'
        )
        Transacao.objects.create(
            remetente=self.user,
            destinatario=self.user,
            valor=Decimal('50.00'),
            tipo_transacao='DEPOSITO'
        )

        url = reverse('transacao-list')
        response = self.api_client.get(url)

        # Verifica se a resposta foi 200 OK e se há 2 transações listadas
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filtrar_transacoes_por_tipo(self):
        """Teste filtrar transações por tipo"""
        # Criar transações de diferentes tipos
        Transacao.objects.create(
            remetente=self.user,
            destinatario=self.user,
            valor=Decimal('100.00'),
            tipo_transacao='DEPOSITO'
        )
        destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        Transacao.objects.create(
            remetente=self.user,
            destinatario=destinatario,
            valor=Decimal('50.00'),
            tipo_transacao='TRANSFERENCIA'
        )

        url = reverse('transacao-list')
        response = self.api_client.get(f"{url}?tipo=DEPOSITO")

        # Verifica se apenas 1 transação do tipo "DEPOSITO" foi retornada
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo_transacao'], 'DEPOSITO')
