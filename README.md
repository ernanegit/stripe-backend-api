# 🧪 Gateway Stripe Sandbox - Versão Completa

[![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=Stripe&logoColor=white)](https://stripe.com)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

Ambiente completo de testes para integração com Stripe usando Django, com suporte a **Cartões**, **PIX** e **Boletos** bancários.

## 🚀 Funcionalidades Implementadas

### ✅ Pagamentos com Cartão
- Cartões de teste do Stripe (sucesso, falha, 3D Secure)
- Validação de endereço brasileiro completo
- Processamento instantâneo
- Webhooks funcionais

### ✅ Geração de Boletos
- **NOVA FUNCIONALIDADE:** Boletos bancários via Stripe
- Validação de CPF/CNPJ com máscara automática
- Endereço de cobrança obrigatório
- Expiração configurável (3 dias úteis)
- Interface totalmente brasileira

### ⚠️ PIX (Em Desenvolvimento)
- Interface preparada para PIX
- **PROBLEMA IDENTIFICADO:** Funcionalidade não operacional
- Necessita revisão na integração com Stripe
- Simulação de QR Code implementada

### 🔧 Recursos Administrativos
- Interface admin Django completa
- Histórico detalhado de transações
- Logs de webhooks para debug
- Status de pagamento em tempo real

## 🛠️ Tecnologias

- **Django 4.2.7** - Framework web Python
- **Stripe 7.8.0** - Gateway de pagamento
- **ngrok** - Túnel para webhooks locais
- **SQLite** - Banco de dados para desenvolvimento
- **CSS/JavaScript** - Interface responsiva

## ⚡ Setup Rápido

### 1. Clone e Configure o Ambiente
```bash
# Clone o repositório
git clone <seu-repositorio>
cd gateway-stripe-sandbox

# Crie e ative virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env
```

Edite o `.env` com suas credenciais do Stripe:
```env
DEBUG=True
SECRET_KEY=sua-secret-key-django-aqui

# Stripe Test Keys (https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Execute Migrações e Configure
```bash
# Execute migrações
python manage.py makemigrations
python manage.py migrate

# Crie superusuário
python manage.py createsuperuser

# Crie produtos de exemplo
python manage.py shell
```

No shell Django:
```python
from payments.models import Product

produtos = [
    {'name': 'Curso Python Avançado', 'description': 'Curso completo de Python com Django', 'price': 197.00},
    {'name': 'E-book Stripe Brasil', 'description': 'Guia definitivo do Stripe no Brasil', 'price': 47.90},
    {'name': 'Consultoria 1h', 'description': 'Mentoria personalizada em pagamentos', 'price': 250.00},
    {'name': 'Workshop Boletos', 'description': 'Como implementar boletos com Stripe', 'price': 97.00},
]

for p in produtos:
    Product.objects.get_or_create(name=p['name'], defaults=p)
    print(f"✅ {p['name']} criado")

exit()
```

### 4. Execute o Projeto

**Windows (Recomendado):**
```bash
.\run_ernane.bat
```

**Manual:**
```bash
python manage.py runserver
```

## 🧪 Testando o Sistema

### 💳 Cartões de Teste

| Cenário | Número do Cartão | CVC | Data | Resultado |
|---------|------------------|-----|------|-----------|
| ✅ **Sucesso** | `4242 4242 4242 4242` | `123` | `12/25` | Aprovado |
| ❌ **Recusado** | `4000 0000 0000 0002` | `123` | `12/25` | Negado |
| 🔐 **3D Secure** | `4000 0000 0000 3220` | `123` | `12/25` | Autenticação |
| 💸 **Sem Saldo** | `4000 0000 0000 9995` | `123` | `12/25` | Insuficiente |

### 📄 Boletos de Teste

**CPF/CNPJ para Teste:**
- CPF: `12345678901` (formato automático: 123.456.789-01)
- CNPJ: `12345678000100` (formato automático: 12.345.678/0001-00)

**Endereços de Teste:**
- CEP: `01310-100` (Av. Paulista, São Paulo)
- CEP: `20040-020` (Centro, Rio de Janeiro)

### 🏦 PIX (Não Funcional)
⚠️ **Status:** Em desenvolvimento - necessita correção na integração

### Fluxo de Teste Completo:
1. Acesse: http://127.0.0.1:8000
2. Clique "🔐 Login Sandbox"
3. Escolha um produto → "🛒 Comprar Agora"
4. Selecione método de pagamento:
   - **Cartão:** Use cartões de teste
   - **Boleto:** Preencha dados brasileiros
   - **PIX:** ⚠️ Não funcional (em correção)
5. Complete o pagamento
6. Verifique resultado na página de sucesso

## 🔗 Configuração de Webhooks

### Setup com ngrok:

1. **Instale ngrok:** https://ngrok.com/download

2. **Configure authtoken:**
   ```bash
   ngrok authtoken SEU_TOKEN
   ```

3. **Execute ngrok:**
   ```bash
   ngrok http 8000
   ```

4. **Configure no Stripe Dashboard:**
   - URL: `https://seu-ngrok.ngrok.io/webhook/stripe/`
   - Eventos selecionados:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `payment_intent.requires_action`
     - `payment_intent.canceled`
     - `payment_intent.processing`

## 📊 Interface Administrativa

**Acesso:** http://127.0.0.1:8000/admin/

### Funcionalidades Admin:
- **📦 Produtos:** Cadastro e gerenciamento do catálogo
- **💳 Pagamentos:** Histórico completo com status coloridos
- **🔗 Webhooks:** Log detalhado de eventos recebidos
- **👥 Usuários:** Gerenciamento de contas de teste

### Status de Pagamento:
- 🟡 **Pendente** - Aguardando processamento
- 🔵 **Processando** - Em andamento
- 🟢 **Aprovado** - Pagamento concluído
- 🔴 **Falhou** - Transação recusada
- ⚪ **Cancelado** - Cancelado pelo usuário
- 🟠 **Requer Ação** - Necessita autenticação

## 📁 Estrutura do Projeto

```
gateway-stripe-sandbox/
├── 📄 manage.py
├── 📄 requirements.txt
├── 📄 .env.example
├── 📄 run_ernane.bat           # Script automatizado Windows
├── 📁 stripe_sandbox/          # Configurações Django
│   ├── 📄 settings.py         # Configurações principais
│   ├── 📄 urls.py             # URLs raiz
│   └── 📄 wsgi.py             # WSGI config
├── 📁 payments/                # App principal
│   ├── 📄 models.py           # Product, Payment, WebhookEvent
│   ├── 📄 views.py            # Lógica de pagamento
│   ├── 📄 admin.py            # Interface administrativa
│   ├── 📄 urls.py             # Rotas do app
│   └── 📁 migrations/         # Migrações do banco
├── 📁 templates/               # Templates HTML
│   └── 📁 payments/
│       ├── 📄 base.html       # Layout base
│       ├── 📄 index.html      # Página inicial
│       ├── 📄 checkout.html   # Checkout (NOVO: boletos)
│       ├── 📄 success.html    # Página de sucesso
│       ├── 📄 history.html    # Histórico
│       └── 📄 payment_detail.html # Detalhes
└── 📁 static/                  # Arquivos estáticos
```

## 🔧 Comandos Úteis

### Gerenciamento do Banco:
```bash
# Reset completo do banco
rm db.sqlite3
python manage.py migrate

# Nova migração
python manage.py makemigrations payments
python manage.py migrate

# Verificar migrações
python manage.py showmigrations
```

### Debug e Desenvolvimento:
```bash
# Shell interativo Django
python manage.py shell

# Executar testes
python manage.py test

# Coletar arquivos estáticos
python manage.py collectstatic

# Verificar configuração
python manage.py check
```

### Logs e Monitoramento:
```bash
# Ver logs em tempo real (se configurado)
tail -f logs/django.log

# Debug do Stripe no shell
python manage.py shell
>>> import stripe
>>> stripe.api_key = 'sk_test_...'
>>> stripe.Product.list()
```

## 🐛 Problemas Conhecidos e Soluções

### ❌ PIX Não Funcional
**Problema:** Interface criada mas integração não operacional
**Status:** 🔧 Em correção
**Workaround:** Use cartões ou boletos para testes

### ⚠️ Erro de Authtoken (ngrok)
**Solução:**
```bash
ngrok authtoken SEU_TOKEN_DO_NGROK
```

### ⚠️ Erro de Chaves Stripe
**Verificação:** Certifique-se de usar chaves de **teste** (pk_test_, sk_test_)

### ⚠️ Webhook Não Recebe Eventos
**Soluções:**
1. Verificar se ngrok está ativo
2. Confirmar URL no Stripe Dashboard
3. Validar `STRIPE_WEBHOOK_SECRET` no .env
4. Testar endpoint: `curl -X POST https://seu-ngrok.ngrok.io/webhook/stripe/`

### ⚠️ Erro de Migração
```bash
python manage.py migrate --fake payments zero
python manage.py migrate
```

## 📚 Recursos e Documentação

### Stripe:
- **Documentação Oficial:** https://stripe.com/docs
- **Cartões de Teste:** https://stripe.com/docs/testing#cards
- **Dashboard Teste:** https://dashboard.stripe.com/test
- **Webhooks Guide:** https://stripe.com/docs/webhooks

### Django:
- **Documentação:** https://docs.djangoproject.com/
- **Tutorial:** https://docs.djangoproject.com/en/4.2/intro/tutorial01/

### Ferramentas:
- **ngrok:** https://ngrok.com/docs
- **Git:** https://git-scm.com/docs

## 🚀 Próximas Implementações

### 🔄 Em Desenvolvimento:
- [ ] **Correção do PIX** - Revisar integração com Stripe
- [ ] **Webhook melhorado** - Mais eventos e logs
- [ ] **Interface mobile** - Responsividade aprimorada
- [ ] **Testes automatizados** - Cobertura completa

### 💡 Funcionalidades Planejadas:
- [ ] **Assinaturas** - Pagamentos recorrentes
- [ ] **Cupons de desconto** - Sistema promocional
- [ ] **Multi-vendedores** - Marketplace
- [ ] **Relatórios avançados** - Analytics detalhados
- [ ] **API REST** - Endpoints para integrações
- [ ] **Docker** - Containerização
- [ ] **Deployment** - Heroku/AWS

## 🤝 Como Contribuir

### Para Desenvolvedores:

1. **Fork o projeto**
   ```bash
   git clone https://github.com/seu-usuario/gateway-stripe-sandbox.git
   ```

2. **Crie uma branch para feature**
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

3. **Desenvolva e teste**
   ```bash
   # Faça suas alterações
   python manage.py test
   ```

4. **Commit e Push**
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   git push origin feature/nova-funcionalidade
   ```

5. **Abra Pull Request**

### 🐛 Reportar Bugs:
- Use as **Issues** do GitHub
- Inclua prints e logs
- Descreva passos para reproduzir

### 💡 Sugerir Melhorias:
- Abra uma **Discussion** no repositório
- Explique o caso de uso
- Proponha implementação

## 📝 Changelog

### v2.0.0 (Atual) - Boletos Implementados
- ✅ **Adicionado:** Suporte completo a boletos bancários
- ✅ **Adicionado:** Validação de CPF/CNPJ com máscaras
- ✅ **Adicionado:** Auto-preenchimento de endereço via CEP
- ✅ **Melhorado:** Interface de checkout mais intuitiva
- ✅ **Melhorado:** Validação de campos obrigatórios
- ❌ **Conhecido:** PIX não funcional (será corrigido em v2.1.0)

### v1.0.0 - Versão Base
- ✅ Pagamentos com cartão
- ✅ Webhooks básicos
- ✅ Interface administrativa
- ✅ Histórico de transações

## 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Ernane** - [@ernanegit](https://github.com/ernanegit)

- 💼 LinkedIn: [seu-linkedin]
- 📧 Email: [seu-email]
- 🌐 Site: [seu-site]

---

## 🎯 Status do Projeto

| Funcionalidade | Status | Observações |
|---------------|--------|-------------|
| 💳 **Cartões** | ✅ Funcional | Todos os cenários testados |
| 📄 **Boletos** | ✅ Funcional | Implementação completa |
| 🏦 **PIX** | ❌ Em Correção | Interface pronta, integração pendente |
| 🔗 **Webhooks** | ✅ Funcional | Eventos principais cobertos |
| 📊 **Admin** | ✅ Funcional | Interface completa |
| 📱 **Mobile** | ⚠️ Básico | Responsivo, melhorias planejadas |

⭐ **Dê uma estrela se este projeto te ajudou!**

🐛 **Encontrou um bug?** Abra uma issue!

💡 **Tem uma ideia?** Compartilhe conosco!

---

*Última atualização: Junho 2025*