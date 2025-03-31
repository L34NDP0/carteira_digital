from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from carteira.models import Carteira, Transacao
from django.urls import reverse


class FluxoOperacionalTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Criar usuário e autenticar
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.client.force_authenticate(user=self.user)

        # Criar destinatário para transferências
        self.destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        self.carteira_destinatario = Carteira.objects.create(
            usuario=self.destinatario
        )

    def test_fluxo_completo_operacoes(self):
        """Teste do fluxo completo de operações: depósito, transferência e consulta"""
        
        # 1. Realizar depósito
        deposito_url = reverse('carteira-deposito')
        deposito_response = self.client.post(
            deposito_url,
            {'valor': '1000.00'},
            format='json'
        )
        self.assertEqual(deposito_response.status_code, 200)
        
        # Verificar saldo após depósito
        self.carteira.refresh_from_db()
        self.assertEqual(self.carteira.saldo, Decimal('1000.00'))

        # 2. Realizar transferência
        transferencia_url = reverse('carteira-transferencia')
        transferencia_response = self.client.post(
            transferencia_url,
            {
                'destinatario_username': 'destinatario',
                'valor': '300.00'
            },
            format='json'
        )
        self.assertEqual(transferencia_response.status_code, 200)

        # Verificar saldos após transferência
        self.carteira.refresh_from_db()
        self.carteira_destinatario.refresh_from_db()
        self.assertEqual(self.carteira.saldo, Decimal('700.00'))
        self.assertEqual(self.carteira_destinatario.saldo, Decimal('300.00'))

        # 3. Verificar histórico de transações
        transacoes_url = reverse('transacao-list')
        transacoes_response = self.client.get(transacoes_url)
        self.assertEqual(transacoes_response.status_code, 200)
        self.assertEqual(len(transacoes_response.data), 2)  # Depósito e transferência

    def test_cenarios_erro(self):
        """Teste de cenários de erro comuns"""
        
        # 1. Tentar transferir sem saldo
        transferencia_url = reverse('carteira-transferencia')
        response = self.client.post(
            transferencia_url,
            {
                'destinatario_username': 'destinatario',
                'valor': '100.00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['erro'], 'Saldo insuficiente')

        # 2. Tentar transferir para usuário inexistente
        response = self.client.post(
            transferencia_url,
            {
                'destinatario_username': 'naoexiste',
                'valor': '100.00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 404)

        # 3. Tentar transferir para si mesmo
        response = self.client.post(
            transferencia_url,
            {
                'destinatario_username': 'testuser',
                'valor': '100.00'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)