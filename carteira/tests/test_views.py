from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from carteira.models import Carteira, Transacao


class UsuarioViewSetTest(APITestCase):
    def test_criar_usuario_sucesso(self):
        """Teste criar usuário com sucesso"""
        url = reverse('usuario-list')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CarteiraViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.client.force_authenticate(user=self.user)

    def test_deposito_sucesso(self):
        """Teste realizar depósito com sucesso"""
        url = reverse('carteira-deposito')
        data = {'valor': '100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.carteira.refresh_from_db()
        self.assertEqual(self.carteira.saldo, Decimal('100.00'))

    def test_deposito_valor_negativo(self):
        """Teste tentar realizar depósito com valor negativo"""
        url = reverse('carteira-deposito')
        data = {'valor': '-100.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transferencia_sucesso(self):
        """Teste realizar transferência com sucesso"""
        destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        Carteira.objects.create(usuario=destinatario)
        
        # Primeiro fazer um depósito
        self.carteira.saldo = Decimal('100.00')
        self.carteira.save()

        url = reverse('carteira-transferencia')
        data = {
            'destinatario_username': 'destinatario',
            'valor': '50.00'
        }
        response = self.client.post(url, data, format='json')
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
            'valor': '100.00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['erro'], 'Saldo insuficiente')


class TransacaoViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.client.force_authenticate(user=self.user)

    def test_listar_transacoes(self):
        """Teste listar transações do usuário"""
        # Criar algumas transações
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
        response = self.client.get(url)
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
        response = self.client.get(f"{url}?tipo=DEPOSITO")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo_transacao'], 'DEPOSITO')