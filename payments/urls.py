from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/pay/<uuid:order_number>/', views.mpesa_pay, name='mpesa_pay'),
    path('mpesa/status/<uuid:order_number>/', views.mpesa_status, name='mpesa_status'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),

    path('paystack/pay/<uuid:order_number>/', views.paystack_pay, name='paystack_pay'),
    path('paystack/verify/<uuid:order_number>/', views.paystack_verify, name='paystack_verify'),
]
