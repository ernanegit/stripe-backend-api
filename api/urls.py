from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health Check
    path('health/', views.health_check, name='health_check'),
    
    # Auth
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/sandbox-login/', views.sandbox_login, name='sandbox_login'),
    
    # Config
    path('config/stripe/', views.stripe_config, name='stripe_config'),
    
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/create-intent/', views.create_payment_intent, name='create_payment_intent'),
]