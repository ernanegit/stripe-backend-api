# 🧪 Gateway Stripe Sandbox

Ambiente completo de testes para integração com Stripe usando Django.

![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=Stripe&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🚀 Features

- ✅ **Pagamentos com cartão** (sucesso, falha, 3D Secure)
- ✅ **Simulação PIX** (ambiente de teste)
- ✅ **Webhooks funcionais** com ngrok
- ✅ **Interface admin** completa
- ✅ **Logs detalhados** de transações
- ✅ **Cartões de teste** pré-configurados
- ✅ **Ambiente sandbox** 100% seguro

## 🛠️ Tecnologias

- **Django 4.2.7** - Framework web
- **Stripe 7.8.0** - Gateway de pagamento
- **ngrok** - Túnel para webhooks
- **SQLite** - Banco de dados (desenvolvimento)
- **Bootstrap CSS** - Interface responsiva

## ⚡ Setup Rápido

### 1. Clone o projeto:
```bash
git clone https://github.com/ernanegit/gateway-stripe-sandbox.git
cd gateway-stripe-sandbox
```

### 2. Crie virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate
```

### 3. Instale dependências:
```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente:
```bash
# Copie e configure o .env
cp .env.example .env
```

Edite o `.env` com suas chaves do Stripe:
```env
DEBUG=True
SECRET_KEY=sua-secret-key-django

# Stripe Test Keys (https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_51...
STRIPE_SECRET_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 5. Execute migrações:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Crie produtos de exemplo:
```bash
python manage.py shell
```

```python
from payments.models import Product

produtos = [
    {'name': 'Curso Python', 'description': 'Curso completo de Python', 'price': 97.00},
    {'name': 'E-book Django', 'description': 'Guia prático do Django', 'price': 47.90},
    {'name': 'Consultoria 1h', 'description': 'Mentoria personalizada', 'price': 150.00},
]

for p in produtos:
    Product.objects.get_or_create(name=p['name'], defaults=p)
    print(f"✅ {p['name']} criado")
```

### 7. Execute o projeto:

**Windows:**
```bash
.\run_ernane.bat
```

**Linux/Mac:**
```bash
python manage.py runserver
```

## 🧪 Testando Pagamentos

### Cartões de Teste:

| Cenário | Número | CVC | Data | Resultado |
|---------|--------|-----|------|-----------|
| ✅ **Sucesso** | `4242 4242 4242 4242` | `123` | `12/25` | Aprovado |
| ❌ **Falha** | `4000 0000 0000 0002` | `123` | `12/25` | Recusado |
| 🔐 **3D Secure** | `4000 0000 0000 3220` | `123` | `12/25` | Requer autenticação |
| 💸 **Sem saldo** | `4000 0000 0000 9995` | `123` | `12/25` | Saldo insuficiente |

### Fluxo de Teste:
1. Acesse: http://127.0.0.1:8000
2. Clique "Login Sandbox"
3. Escolha um produto → "Comprar Agora"
4. Use um dos cartões de teste
5. Verifique o resultado

## 🔗 Webhooks

### Configuração com ngrok:

1. **Instale ngrok:** https://ngrok.com/download
2. **Configure authtoken:**
   ```bash
   ngrok authtoken SEU_TOKEN
   ```
3. **Execute ngrok:**
   ```bash
   ngrok http 8000
   ```
4. **Configure webhook no Stripe:**
   - URL: `https://seu-ngrok.ngrok.io/webhook/stripe/`
   - Eventos: `payment_intent.*`

### Eventos Monitorados:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `payment_intent.requires_action`
- `payment_intent.canceled`

## 📊 Admin Dashboard

Acesse: http://127.0.0.1:8000/admin/

**Funcionalidades:**
- 📦 **Produtos:** Gerenciar catálogo
- 💳 **Pagamentos:** Histórico completo
- 🔗 **Webhooks:** Log de eventos
- 👥 **Usuários:** Gerenciar contas

## 📁 Estrutura do Projeto

```
gateway-stripe-sandbox/
├── 📄 manage.py
├── 📄 requirements.txt
├── 📄 README.md
├── 📁 stripe_sandbox/        # Configurações Django
├── 📁 payments/              # App principal
│   ├── 📄 models.py         # Product, Payment, WebhookEvent
│   ├── 📄 views.py          # Lógica de pagamento
│   ├── 📄 admin.py          # Interface admin
│   └── 📄 urls.py           # Rotas
├── 📁 templates/            # Templates HTML
│   └── 📁 payments/
│       ├── 📄 base.html     # Layout base
│       ├── 📄 index.html    # Página inicial
│       ├── 📄 checkout.html # Checkout
│       └── 📄 success.html  # Sucesso
└── 📁 static/               # Arquivos estáticos
```

## 🔧 Comandos Úteis

```bash
# Limpar migrações
python manage.py migrate --fake payments zero
python manage.py showmigrations

# Reset do banco
rm db.sqlite3
python manage.py migrate

# Coletar static files
python manage.py collectstatic

# Executar testes
python manage.py test

# Shell interativo
python manage.py shell
```

## 🐛 Troubleshooting

### Erro de Authtoken (ngrok):
```bash
ngrok authtoken SEU_TOKEN_DO_NGROK
```

### Erro de Chave Stripe:
Verifique se está usando chaves de **teste** (pk_test_, sk_test_)

### Erro de Migração:
```bash
python manage.py makemigrations payments
python manage.py migrate
```

### Webhook não funciona:
1. Verifique se ngrok está rodando
2. Confirme URL no Stripe Dashboard
3. Verifique `STRIPE_WEBHOOK_SECRET` no .env

## 📚 Recursos

- **Documentação Stripe:** https://stripe.com/docs
- **Cartões de Teste:** https://stripe.com/docs/testing#cards
- **Django Docs:** https://docs.djangoproject.com/
- **ngrok Docs:** https://ngrok.com/docs

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Ernane** - [@ernanegit](https://github.com/ernanegit)

---

⭐ **Dê uma estrela se este projeto te ajudou!**