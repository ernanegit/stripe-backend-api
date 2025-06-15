# payments/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import stripe
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_product_id = models.CharField(max_length=200, blank=True)
    stripe_price_id = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - R$ {self.price}"
    
    def get_absolute_url(self):
        return reverse('payments:product_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Cria produto no Stripe automaticamente
        if not self.stripe_product_id:
            try:
                stripe_product = stripe.Product.create(
                    name=self.name,
                    description=self.description,
                    metadata={'django_id': str(self.id) if self.id else 'new'}
                )
                self.stripe_product_id = stripe_product.id
                
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=int(self.price * 100),  # Em centavos
                    currency='brl',
                )
                self.stripe_price_id = stripe_price.id
                
                logger.info(f"Produto criado no Stripe: {stripe_product.id}")
                
            except stripe.error.StripeError as e:
                logger.error(f"Erro ao criar produto no Stripe: {e}")
        
        super().save(*args, **kwargs)

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('succeeded', 'Aprovado'),
        ('failed', 'Falhou'),
        ('canceled', 'Cancelado'),
        ('requires_action', 'Requer Ação'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Cartão'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Stripe IDs
    stripe_payment_intent_id = models.CharField(max_length=200, unique=True)
    stripe_customer_id = models.CharField(max_length=200, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='brl')
    payment_method_type = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    stripe_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pagamento #{self.id} - {self.user.username} - {self.get_status_display()}"
    
    def get_absolute_url(self):
        return reverse('payments:payment_detail', kwargs={'pk': self.pk})

class WebhookEvent(models.Model):
    """Log de eventos de webhook para debug"""
    stripe_event_id = models.CharField(max_length=200, unique=True)
    event_type = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}"