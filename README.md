 # API de Carteira Digital

Uma API RESTful robusta para gerenciamento de carteira digital, desenvolvida com Django REST Framework, permitindo transferências seguras e controle financeiro.

## 🚀 Funcionalidades Principais

- **Gestão de Usuários**
  - Cadastro seguro de usuários
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

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Django 5.1
- Django REST Framework
- PostgreSQL
- JWT para autenticação e egurança
- Pytest Testes automatizados

## 📋 Endpoints Principais

### Autenticação
```http
POST /api/token/
POST /api/token/refresh/
```

### Usuários
```http
POST /api/usuarios/
```

### Carteira
```http
GET /api/carteiras/
POST /api/carteiras/deposito/
POST /api/carteiras/transferencia/
```

### Transações
```http
GET /api/transacoes/
```

## 🔒 Segurança

- Implementação de transações atômicas
- Validações rigorosas de dados
- Proteção contra race conditions
- Testes de integração abrangentes

## 🧪 Testes

O projeto possui uma suíte completa de testes, incluindo:
- Testes unitários
- Testes de integração
- Testes de modelos
- Testes de API

Cobertura de testes superior a 90%.

## 💡 Diferenciais Técnicos

1. **Arquitetura Robusta**
   - Separação clara de responsabilidades
   - Código modular e reutilizável
   - Fácil manutenção e escalabilidade

2. **Boas Práticas**
   - Código limpo e bem documentado
   - Seguindo princípios SOLID
   - Padrões REST

3. **Performance**
   - Queries otimizadas
   - Uso eficiente do banco de dados
   - Implementação de filtros e ordenação

## 🚀 Como Executar

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente
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

## 👨‍💻 Desenvolvimento

Este projeto foi desenvolvido com foco em:
- Qualidade de código
- Segurança
- Escalabilidade
- Manutenibilidade
- Testes automatizados

## 🤝 Contribuição

O projeto segue as melhores práticas de desenvolvimento e está aberto a melhorias e sugestões.
