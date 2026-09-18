from django.contrib import admin
from .models import MpesaTransaction, PaystackTransaction


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'phone_number', 'amount', 'result_code', 'mpesa_receipt_number', 'created_at')
    list_filter = ('result_code',)
    search_fields = ('checkout_request_id', 'mpesa_receipt_number', 'phone_number')
    readonly_fields = [f.name for f in MpesaTransaction._meta.fields]


@admin.register(PaystackTransaction)
class PaystackTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'reference', 'amount', 'verified', 'created_at')
    list_filter = ('verified',)
    search_fields = ('reference', 'email')
    readonly_fields = [f.name for f in PaystackTransaction._meta.fields]
