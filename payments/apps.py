# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.index, name='index'),
    path('auto-login/', views.auto_login, name='auto_login'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('history/', views.payment_history, name='payment_history'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]