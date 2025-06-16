# payments/views.py - ARQUIVO COMPLETO CORRIGIDO
import stripe
import json
import logging
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils import timezone
from .models import Product, Payment, WebhookEvent

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

def index(request):
    """Página inicial com produtos"""
    products = Product.objects.filter(active=True)
    return render(request, 'payments/index.html', {'products': products})

def auto_login(request):
    """Login automático para sandbox (apenas para desenvolvimento!)"""
    if not settings.DEBUG:
        return redirect('admin:index')
    
    # Cria ou pega usuário de teste
    user, created = User.objects.get_or_create(
        username='sandbox_user',
        defaults={
            'email': 'sandbox@example.com',
            'first_name': 'Usuário',
            'last_name': 'Sandbox'
        }
    )
    
    login(request, user)
    messages.success(request, f'Login automático como {user.username}')
    return redirect('payments:index')

@login_required
def product_detail(request, pk):
    """Detalhes do produto"""
    product = get_object_or_404(Product, pk=pk, active=True)
    return render(request, 'payments/product_detail.html', {'product': product})

@login_required
def checkout(request, product_id):
    """Página de checkout com suporte a cartão, PIX e boleto"""
    product = get_object_or_404(Product, id=product_id, active=True)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method = data.get('payment_method', 'card')
            
            logger.info(f"Iniciando checkout para método: {payment_method}, produto: {product.name}")
            
            # Cria ou obtém customer do Stripe
            customer = None
            try:
                # Busca customer existente
                customers = stripe.Customer.list(email=request.user.email, limit=1)
                if customers.data:
                    customer = customers.data[0]
                else:
                    # Cria novo customer
                    customer = stripe.Customer.create(
                        email=request.user.email,
                        name=request.user.get_full_name() or request.user.username,
                        metadata={'django_user_id': request.user.id}
                    )
                    logger.info(f"Customer criado: {customer.id}")
            
            except stripe.error.StripeError as e:
                logger.error(f"Erro ao criar customer: {e}")
                return JsonResponse({'error': str(e)}, status=400)
            
            # Configuração específica para cada método de pagamento
            if payment_method == 'pix':
                # PIX requer configurações específicas
                intent_data = {
                    'amount': int(product.price * 100),  # Em centavos
                    'currency': 'brl',
                    'payment_method_types': ['pix'],
                    'customer': customer.id if customer else None,
                    'payment_method_options': {
                        'pix': {
                            'expires_after_seconds': 86400  # 24 horas para expirar
                        }
                    },
                    'confirmation_method': 'automatic',
                    'confirm': True,  # Confirma automaticamente
                    'return_url': request.build_absolute_uri(f'/success/{0}/'),  # Será atualizado
                    'metadata': {
                        'product_id': product.id,
                        'user_id': request.user.id,
                        'django_payment_method': payment_method
                    }
                }
            elif payment_method == 'boleto':
                logger.info("=== CONFIGURANDO BOLETO COM AUTOMATIC ===")
                logger.info(f"User: {request.user.username}, Email: {request.user.email}")
                logger.info(f"Product: {product.name}, Price: {product.price}")
                
                # CORREÇÃO DEFINITIVA: SEMPRE usar automatic para boleto
                intent_data = {
                    'amount': int(product.price * 100),  # Em centavos
                    'currency': 'brl',
                    'payment_method_types': ['boleto'],
                    'customer': customer.id if customer else None,
                    'payment_method_options': {
                        'boleto': {
                            'expires_after_days': 3
                        }
                    },
                    # FUNDAMENTAL: usar automatic para permitir confirmação no frontend
                    'confirmation_method': 'automatic',
                    'metadata': {
                        'product_id': str(product.id),
                        'user_id': str(request.user.id),
                        'django_payment_method': payment_method,
                        'user_email': request.user.email
                    }
                }
                
                logger.info(f"Intent data para boleto: {intent_data}")
                logger.info("=== BOLETO CONFIGURADO COM AUTOMATIC ===")
            else:
                # Configuração para cartão (padrão)
                intent_data = {
                    'amount': int(product.price * 100),
                    'currency': 'brl',
                    'payment_method_types': ['card'],
                    'customer': customer.id if customer else None,
                    # TAMBÉM garantir automatic para cartão
                    'confirmation_method': 'automatic',
                    'metadata': {
                        'product_id': product.id,
                        'user_id': request.user.id,
                        'django_payment_method': payment_method
                    }
                }
            
            # Cria Payment Intent
            logger.info("Criando Payment Intent...")
            intent = stripe.PaymentIntent.create(**intent_data)
            logger.info(f"Payment Intent criado com sucesso: {intent.id}, status: {intent.status}")
            logger.info(f"Confirmation method: {intent.confirmation_method}")  # LOG PARA VERIFICAR
            
            # Salva pagamento no banco
            payment = Payment.objects.create(
                user=request.user,
                product=product,
                stripe_payment_intent_id=intent.id,
                stripe_customer_id=customer.id if customer else '',
                amount=product.price,
                payment_method_type=payment_method,
                status='pending'
            )
            
            # Atualiza return_url com o ID do pagamento real para PIX
            if payment_method == 'pix':
                stripe.PaymentIntent.modify(
                    intent.id,
                    return_url=request.build_absolute_uri(f'/success/{payment.id}/')
                )
            
            logger.info(f"Payment Intent criado: {intent.id} para usuário {request.user.username}")
            
            response_data = {
                'client_secret': intent.client_secret,
                'payment_id': payment.id,
                'payment_method': payment_method
            }
            
            # Para PIX, incluir informações adicionais
            if payment_method == 'pix' and intent.status == 'requires_action':
                response_data['requires_action'] = True
                response_data['next_action'] = intent.next_action
            
            # Para Boleto, client_secret é suficiente (frontend vai confirmar)
            if payment_method == 'boleto':
                response_data['status'] = intent.status
            
            logger.info(f"Response data: {response_data}")
            return JsonResponse(response_data)
            
        except stripe.error.StripeError as e:
            logger.error(f"Erro Stripe: {e}")
            logger.error(f"Detalhes do erro: {e.user_message if hasattr(e, 'user_message') else 'N/A'}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            logger.error(f"Traceback: ", exc_info=True)
            return JsonResponse({'error': 'Erro interno do servidor'}, status=500)
    
    # GET request - mostra página de checkout
    context = {
        'product': product,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'payments/checkout.html', context)

@login_required
def payment_success(request, payment_id):
    """Página de sucesso"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Verifica status no Stripe para garantir que está atualizado
    try:
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
        if intent.status != payment.status:
            payment.status = intent.status
            if intent.status == 'succeeded':
                payment.paid_at = timezone.now()
            payment.save()
            logger.info(f"Status do pagamento {payment.id} atualizado para {intent.status}")
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao verificar pagamento: {e}")
    
    return render(request, 'payments/success.html', {'payment': payment})

@login_required
def payment_history(request):
    """Histórico de pagamentos"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})

@login_required
def payment_detail(request, pk):
    """Detalhes de um pagamento específico"""
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    
    # Busca dados atualizados no Stripe
    stripe_data = None
    try:
        stripe_data = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
    except stripe.error.StripeError as e:
        logger.error(f"Erro ao buscar dados do Stripe: {e}")
    
    return render(request, 'payments/payment_detail.html', {
        'payment': payment,
        'stripe_data': stripe_data
    })

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Webhook aprimorado para cartão, PIX e boleto"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Payload inválido no webhook")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Assinatura inválida no webhook")
        return HttpResponse(status=400)
    
    # Log do evento
    webhook_event, created = WebhookEvent.objects.get_or_create(
        stripe_event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data'],
            'processed': False
        }
    )
    
    if not created and webhook_event.processed:
        logger.info(f"Evento já processado: {event['id']}")
        return HttpResponse(status=200)
    
    logger.info(f"Processando webhook: {event['type']} - {event['id']}")
    
    # Processa eventos (incluindo novos eventos para PIX e Boleto)
    try:
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_succeeded(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_failed(event['data']['object'])
        elif event['type'] == 'payment_intent.requires_action':
            handle_payment_requires_action(event['data']['object'])
        elif event['type'] == 'payment_intent.canceled':
            handle_payment_canceled(event['data']['object'])
        elif event['type'] == 'payment_intent.processing':
            handle_payment_processing(event['data']['object'])
        else:
            logger.info(f"Evento não tratado: {event['type']}")
        
        webhook_event.processed = True
        webhook_event.save()
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)

def handle_payment_succeeded(payment_intent):
    """Processa pagamento aprovado"""
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'succeeded'
        payment.paid_at = timezone.now()
        
        # Extrai informações financeiras
        if 'charges' in payment_intent and payment_intent['charges']['data']:
            charge = payment_intent['charges']['data'][0]
            balance_transaction_id = charge.get('balance_transaction')
            
            if balance_transaction_id:
                # Busca detalhes da transação para obter taxas
                try:
                    balance_transaction = stripe.BalanceTransaction.retrieve(balance_transaction_id)
                    payment.stripe_fee = Decimal(str(balance_transaction['fee'])) / 100
                    payment.net_amount = Decimal(str(balance_transaction['net'])) / 100
                except stripe.error.StripeError as e:
                    logger.error(f"Erro ao buscar balance transaction: {e}")
        
        payment.save()
        logger.info(f"Pagamento {payment.id} marcado como aprovado")
        
    except Payment.DoesNotExist:
        logger.error(f"Pagamento não encontrado para intent: {payment_intent['id']}")

def handle_payment_failed(payment_intent):
    """Processa pagamento falhou"""
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'failed'
        payment.save()
        logger.info(f"Pagamento {payment.id} marcado como falhou")
    except Payment.DoesNotExist:
        logger.error(f"Pagamento não encontrado para intent: {payment_intent['id']}")

def handle_payment_requires_action(payment_intent):
    """Processa pagamento que requer ação"""
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'requires_action'
        payment.save()
        logger.info(f"Pagamento {payment.id} requer ação")
    except Payment.DoesNotExist:
        logger.error(f"Pagamento não encontrado para intent: {payment_intent['id']}")

def handle_payment_canceled(payment_intent):
    """Processa pagamento cancelado"""
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'canceled'
        payment.save()
        logger.info(f"Pagamento {payment.id} cancelado")
    except Payment.DoesNotExist:
        logger.error(f"Pagamento não encontrado para intent: {payment_intent['id']}")

def handle_payment_processing(payment_intent):
    """Processa pagamento em andamento (comum para PIX e Boleto)"""
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
        payment.status = 'processing'
        payment.save()
        logger.info(f"Pagamento {payment.id} marcado como processando")
    except Payment.DoesNotExist:
        logger.error(f"Pagamento não encontrado para intent: {payment_intent['id']}")