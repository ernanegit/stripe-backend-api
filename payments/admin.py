

# Register your models here.
# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Payment, WebhookEvent

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'active', 'stripe_product_id', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('stripe_product_id', 'stripe_price_id')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description', 'price', 'active')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_product_id', 'stripe_price_id'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'amount', 'payment_method_type', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method_type', 'created_at')
    search_fields = ('user__username', 'product__name', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'stripe_customer_id', 'stripe_fee', 'net_amount', 'paid_at')
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'succeeded': '#28a745',
            'failed': '#dc3545',
            'canceled': '#6c757d',
            'requires_action': '#fd7e14',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('user', 'product', 'amount', 'currency', 'payment_method_type', 'status')
        }),
        ('Stripe Data', {
            'fields': ('stripe_payment_intent_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Financeiro', {
            'fields': ('stripe_fee', 'net_amount', 'paid_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('stripe_event_id', 'event_type', 'processed', 'created_at')
    list_filter = ('event_type', 'processed', 'created_at')
    search_fields = ('stripe_event_id', 'event_type')
    readonly_fields = ('stripe_event_id', 'event_type', 'data')
    
    def has_add_permission(self, request):
        return False  # Apenas leitura via webhook