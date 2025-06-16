from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Payment, WebhookEvent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 
            'stripe_product_id', 'stripe_price_id', 
            'active', 'created_at'
        ]
        read_only_fields = ['stripe_product_id', 'stripe_price_id', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'product', 'stripe_payment_intent_id',
            'stripe_customer_id', 'amount', 'currency', 
            'payment_method_type', 'status', 'stripe_fee',
            'net_amount', 'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_intent_id', 'stripe_customer_id',
            'stripe_fee', 'net_amount', 'created_at', 'updated_at', 'paid_at'
        ]

class PaymentCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['card', 'pix', 'boleto'],
        default='card'
    )
    billing_details = serializers.JSONField(required=False)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, active=True)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produto não encontrado ou inativo")

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at']