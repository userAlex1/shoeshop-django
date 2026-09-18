from django.db import models
from store.models import Order


class MpesaTransaction(models.Model):
    order = models.ForeignKey(Order, related_name='mpesa_transactions', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # From STK push request
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)

    # From callback
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.CharField(max_length=255, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)

    raw_callback = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"M-Pesa {self.checkout_request_id} - order {self.order.order_number}"


class PaystackTransaction(models.Model):
    order = models.ForeignKey(Order, related_name='paystack_transactions', on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()

    verified = models.BooleanField(default=False)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paystack {self.reference} - order {self.order.order_number}"
