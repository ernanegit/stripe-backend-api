from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from decimal import Decimal
import stripe
import json
import logging

from payments.models import Product, Payment, WebhookEvent
from payments.serializers import (
    ProductSerializer, PaymentSerializer, 
    PaymentCreateSerializer, UserSerializer
)

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Registro de usuário para o sandbox"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=request.data.get('password', 'sandbox123')
        )
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login com token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response(
        {'error': 'Credenciais inválidas'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def sandbox_login(request):
    """Login automático para sandbox"""
    user, created = User.objects.get_or_create(
        username='sandbox_user',
        defaults={
            'email': 'sandbox@example.com',
            'first_name': 'Usuário',
            'last_name': 'Sandbox'
        }
    )
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key
    })

# Product Views
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['active']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

# Payment Views
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payment_method_type']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """Cria Payment Intent no Stripe"""
    serializer = PaymentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(
            id=serializer.validated_data['product_id'], 
            active=True
        )
        payment_method = serializer.validated_data['payment_method']
        billing_details = serializer.validated_data.get('billing_details', {})

        logger.info(f"Criando Payment Intent para {payment_method}, produto: {product.name}")
        
        # Criar ou obter customer do Stripe
        customer = None
        try:
            customers = stripe.Customer.list(email=request.user.email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=request.user.get_full_name() or request.user.username,
                    metadata={'django_user_id': request.user.id}
                )
        except stripe.error.StripeError as e:
            logger.error(f"Erro ao criar customer: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Configuração específica para cada método de pagamento
        intent_data = {
            'amount': int(product.price * 100),  # Em centavos
            'currency': 'brl',
            'customer': customer.id if customer else None,
            'confirmation_method': 'automatic',
            'metadata': {
                'product_id': str(product.id),
                'user_id': str(request.user.id),
                'django_payment_method': payment_method
            }
        }

        if payment_method == 'pix':
            intent_data.update({
                'payment_method_types': ['pix'],
                'payment_method_options': {
                    'pix': {
                        'expires_after_seconds': 86400  # 24 horas
                    }
                }
            })
        elif payment_method == 'boleto':
            intent_data.update({
                'payment_method_types': ['boleto'],
                'payment_method_options': {
                    'boleto': {
                        'expires_after_days': 3
                    }
                }
            })
        else:  # card
            intent_data.update({
                'payment_method_types': ['card']
            })

        # Criar Payment Intent
        intent = stripe.PaymentIntent.create(**intent_data)
        logger.info(f"Payment Intent criado: {intent.id}")

        # Salvar pagamento no banco
        payment = Payment.objects.create(
            user=request.user,
            product=product,
            stripe_payment_intent_id=intent.id,
            stripe_customer_id=customer.id if customer else '',
            amount=product.price,
            payment_method_type=payment_method,
            status='pending'
        )

        return Response({
            'client_secret': intent.client_secret,
            'payment_id': payment.id,
            'payment_method': payment_method,
            'status': intent.status
        })

    except Exception as e:
        logger.error(f"Erro ao criar Payment Intent: {e}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Config View
@api_view(['GET'])
@permission_classes([AllowAny])
def stripe_config(request):
    """Retorna configurações públicas do Stripe"""
    return Response({
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

# Health Check
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check para Railway"""
    return Response({'status': 'healthy'})

# NOVO: Endpoint para criar produtos de exemplo
@api_view(['POST'])
@permission_classes([AllowAny])
def create_sample_products(request):
    """TEMPORÁRIO: Criar produtos de exemplo"""
    
    # Verificar se já existem produtos
    if Product.objects.exists():
        return Response({'error': 'Produtos já existem'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Produtos de exemplo
    produtos = [
        {'name': 'Curso Python Avançado', 'description': 'Curso completo de Python com Django', 'price': 197.00},
        {'name': 'E-book Stripe Brasil', 'description': 'Guia definitivo do Stripe no Brasil', 'price': 47.90},
        {'name': 'Consultoria 1h', 'description': 'Mentoria personalizada em pagamentos', 'price': 250.00},
        {'name': 'Workshop Boletos', 'description': 'Como implementar boletos com Stripe', 'price': 97.00},
    ]
    
    # Criar produtos
    created_products = []
    for produto_data in produtos:
        produto = Product.objects.create(**produto_data)
        created_products.append({
            'id': produto.id,
            'name': produto.name,
            'price': float(produto.price)
        })
    
    return Response({
        'message': f'{len(created_products)} produtos criados com sucesso',
        'products': created_products
    })