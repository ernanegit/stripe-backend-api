from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    # Webhook em payments (sem namespace para evitar conflito)
    path('webhook/stripe/', include('payments.urls')),
]