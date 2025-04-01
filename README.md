# API de Carteira Digital

Uma API RESTful robusta para gerenciamento de carteira digital, desenvolvida com Django REST Framework, permitindo transferências seguras e controle financeiro.

## 🚀 Funcionalidades Principais

- **Gestão de Usuários**
  - Cadastro seguro de usuários
  - Listagem de usuários (autenticado)
  - Criação automática de carteira digital
  - Autenticação via JWT (JSON Web Tokens)

- **Operações Financeiras**
  - Depósitos
  - Transferências entre usuários
  - Consulta de saldo
  - Histórico de transações

- **Segurança**
  - Transações atômicas para garantir consistência
  - Validações de saldo e valores
  - Proteção contra saldo negativo
  - Autenticação obrigatória para operações
  - Filtro de superusuários na listagem

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Django 5.1
- Django REST Framework
- PostgreSQL
- JWT para autenticação
- Django Filter para filtros avançados
- Pytest para testes automatizados

## 📋 Endpoints da API

### Autenticação
```http
POST /api/token/
{
    "username": "seu_usuario",
    "password": "sua_senha"
}

POST /api/token/refresh/
{
    "refresh": "seu_token_refresh"
}
```

### Usuários
```http
# Criar usuário (público)
POST /api/usuarios/
{
    "username": "usuario1",
    "email": "usuario1@email.com",
    "password": "senha123"
}

# Listar usuários (requer autenticação)
GET /api/usuarios/
```

### Carteira
```http
# Consultar saldo (autenticado)
GET /api/carteiras/

# Realizar depósito (autenticado)
POST /api/carteiras/deposito/
{
    "valor": "100.00"
}

# Realizar transferência (autenticado)
POST /api/carteiras/transferencia/
{
    "destinatario_username": "usuario2",
    "valor": "50.00"
}
```

### Transações
```http
# Listar transações (autenticado)
GET /api/transacoes/

# Filtrar por tipo
GET /api/transacoes/?tipo=DEPOSITO

# Filtrar por período
GET /api/transacoes/?data_inicio=2024-01-01&data_fim=2024-12-31
```

## 🔒 Segurança e Validações

- **Autenticação**
  - JWT Token para autenticação segura
  - Endpoints protegidos por autenticação
  - Refresh token para renovação de sessão

- **Transações**
  - Transações atômicas (ACID)
  - Validação de saldo suficiente
  - Proteção contra valores negativos
  - Valor mínimo de R$ 0,01

- **Usuários**
  - Senhas armazenadas com hash
  - Filtragem de superusuários
  - Validação de dados

## 🧪 Testes

O projeto possui cobertura completa de testes, incluindo:

- **Testes de Usuários**
  - Criação de usuário
  - Listagem de usuários
  - Validações de autenticação
  - Filtragem de superusuários

- **Testes de Carteira**
  - Depósitos
  - Transferências
  - Validações de saldo
  - Consistência de dados

- **Testes de Transações**
  - Registro de operações
  - Filtros de consulta
  - Validações de valores
  - Integridade dos dados

## 💡 Diferenciais Técnicos

1. **Arquitetura**
   - Separação clara de responsabilidades (models, views, serializers)
   - Código modular e reutilizável
   - Padrões REST
   - Documentação clara

2. **Performance**
   - Queries otimizadas
   - Select for update em transações
   - Índices adequados
   - Paginação de resultados

3. **Manutenibilidade**
   - Código bem documentado
   - Testes automatizados
   - Validações centralizadas
   - Padrões de código consistentes

## 🚀 Como Executar

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente no .env:

4. Execute as migrações:
   ```bash
   python manage.py migrate
   ```
5. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

## 📚 Documentação

A API possui documentação completa dos endpoints, incluindo:
- Descrição detalhada de cada rota
- Exemplos de requisição e resposta
- Códigos de status HTTP
- Tratamento de erros

## 🔍 Exemplos de Uso

### Criar Usuário
```json
POST /api/usuarios/
{
    "username": "usuario1",
    "email": "usuario1@email.com",
    "password": "senha123"
}
```

### Realizar Transferência
```json
POST /api/carteiras/transferencia/
{
    "destinatario_username": "usuario2",
    "valor": "100.00"
}
```



