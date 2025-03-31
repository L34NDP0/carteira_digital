from decimal import Decimal
from django.test import TransactionTestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from carteira.models import Carteira, Transacao
from django.urls import reverse


class FluxoOperacionalTest(TransactionTestCase):
    def setUp(self):
        """Configuração inicial antes de cada teste"""
        self.client = APIClient()
        
        # Criar usuário principal e autenticar
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.carteira = Carteira.objects.create(usuario=self.user)
        self.client.force_authenticate(user=self.user)  # Autentica o usuário na API

        # Criar um destinatário para transferências
        self.destinatario = User.objects.create_user(
            username='destinatario',
            password='testpass123'
        )
        self.carteira_destinatario = Carteira.objects.create(
            usuario=self.destinatario
        )

    def test_fluxo_completo_operacoes(self):
        """Teste do fluxo completo de operações: depósito, transferência e consulta de transações"""
        
        # 1. Realizar depósito
        deposito_url = reverse('carteira-deposito')  # Obtém a URL do endpoint de depósito
        deposito_response = self.client.post(
            deposito_url,
            {'valor': '1000.00'},  # Envia um valor de 1000.00 para depósito
            format='json'
        )
        self.assertEqual(deposito_response.status_code, 200)  # Verifica se a resposta foi bem-sucedida
        
        # Verificar saldo após depósito
        self.carteira.refresh_from_db()  # Atualiza a carteira do banco de dados
        self.assertEqual(self.carteira.saldo, Decimal('1000.00'))  # Saldo deve ser 1000.00

        # 2. Realizar transferência para outro usuário
        transferencia_url = reverse('carteira-transferencia')  # Obtém a URL do endpoint de transferência
        transferencia_response = self.client.post(
            transferencia_url,
            {
                'destinatario_username': 'destinatario',  # Nome do usuário destinatário
                'valor': '300.00'  # Valor a ser transferido
            },
            format='json'
        )
        self.assertEqual(transferencia_response.status_code, 200)  # Verifica se a transferência foi bem-sucedida

        # Verificar saldos após a transferência
        self.carteira.refresh_from_db()
        self.carteira_destinatario.refresh_from_db()
        self.assertEqual(self.carteira.saldo, Decimal('700.00'))  # Remetente deve ter 700.00
        self.assertEqual(self.carteira_destinatario.saldo, Decimal('300.00'))  # Destinatário deve ter 300.00

        # 3. Verificar histórico de transações do usuário autenticado
        transacoes_url = reverse('transacao-list')  # Obtém a URL do endpoint de listagem de transações
        transacoes_response = self.client.get(transacoes_url)
        self.assertEqual(transacoes_response.status_code, 200)  # Verifica se a consulta foi bem-sucedida
        self.assertEqual(len(transacoes_response.data), 2)  # Deve haver duas transações: depósito e transferência
