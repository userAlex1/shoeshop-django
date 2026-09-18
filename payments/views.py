import json
import uuid
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages

from store.models import Order
from store.cart import Cart
from . import mpesa, paystack
from .models import MpesaTransaction, PaystackTransaction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# M-PESA
# ---------------------------------------------------------------------------

def mpesa_pay(request, order_number):
    """Show a 'waiting for STK push' page and trigger the push."""
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        phone = request.POST.get('phone', order.phone)
        try:
            result = mpesa.stk_push(
                phone_number=phone,
                amount=order.total_amount,
                order_number=order.order_number,
            )
        except mpesa.MpesaError as e:
            logger.exception("M-Pesa STK push failed")
            messages.error(request, f"Could not start M-Pesa payment: {e}")
            return render(request, 'payments/mpesa_pay.html', {'order': order})

        # ResponseCode "0" means the request was accepted; the actual
        # payment result arrives later at the callback URL.
        if str(result.get('ResponseCode')) == '0':
            MpesaTransaction.objects.create(
                order=order,
                phone_number=mpesa.format_phone_number(phone),
                amount=order.total_amount,
                merchant_request_id=result.get('MerchantRequestID', ''),
                checkout_request_id=result.get('CheckoutRequestID', ''),
            )
            return render(request, 'payments/mpesa_waiting.html', {
                'order': order,
                'checkout_request_id': result.get('CheckoutRequestID'),
            })
        else:
            messages.error(request, result.get('errorMessage', 'STK push was rejected.'))

    return render(request, 'payments/mpesa_pay.html', {'order': order})


def mpesa_status(request, order_number):
    """
    Polled by JS on the 'waiting' page to check if payment succeeded yet.
    Returns JSON: {"status": "pending"|"paid"|"failed"}
    """
    order = get_object_or_404(Order, order_number=order_number)
    if order.status == Order.STATUS_PAID:
        return JsonResponse({'status': 'paid'})
    if order.status == Order.STATUS_FAILED:
        return JsonResponse({'status': 'failed'})
    return JsonResponse({'status': 'pending'})


@csrf_exempt
def mpesa_callback(request):
    """
    Safaricom POSTs the payment result here. This URL must be a public
    HTTPS URL (use ngrok during development) and set as MPESA_CALLBACK_URL.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.error("Invalid M-Pesa callback payload")
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid payload"})

    logger.info("M-Pesa callback received: %s", data)

    stk_callback = data.get('Body', {}).get('stkCallback', {})
    checkout_request_id = stk_callback.get('CheckoutRequestID')
    result_code = stk_callback.get('ResultCode')
    result_desc = stk_callback.get('ResultDesc')

    try:
        txn = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
    except MpesaTransaction.DoesNotExist:
        logger.error("No matching MpesaTransaction for %s", checkout_request_id)
        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    txn.result_code = result_code
    txn.result_desc = result_desc
    txn.raw_callback = data

    if result_code == 0:
        # Extract the M-Pesa receipt number from CallbackMetadata
        metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
        for entry in metadata:
            if entry.get('Name') == 'MpesaReceiptNumber':
                txn.mpesa_receipt_number = entry.get('Value', '')
        txn.save()
        txn.order.mark_paid()
    else:
        txn.save()
        txn.order.status = Order.STATUS_FAILED
        txn.order.save(update_fields=['status', 'updated_at'])

    # Safaricom expects this exact acknowledgement format
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


# ---------------------------------------------------------------------------
# PAYSTACK (card / bank)
# ---------------------------------------------------------------------------

def paystack_pay(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    reference = f"order-{order.order_number}-{uuid.uuid4().hex[:8]}"

    callback_url = request.build_absolute_uri(
        reverse('payments:paystack_verify', args=[order.order_number])
    )

    try:
        data = paystack.initialize_transaction(
            email=order.email or "customer@example.com",
            amount=order.total_amount,
            reference=reference,
            callback_url=callback_url,
        )
    except paystack.PaystackError as e:
        logger.exception("Paystack init failed")
        messages.error(request, f"Could not start card payment: {e}")
        return redirect('store:checkout')

    PaystackTransaction.objects.create(
        order=order,
        reference=reference,
        amount=order.total_amount,
        email=order.email or "customer@example.com",
    )

    return redirect(data['authorization_url'])


def paystack_verify(request, order_number):
    """Paystack redirects here after checkout, with ?reference=... in the URL."""
    order = get_object_or_404(Order, order_number=order_number)
    reference = request.GET.get('reference')
    txn = get_object_or_404(PaystackTransaction, reference=reference, order=order)

    try:
        data = paystack.verify_transaction(reference)
    except paystack.PaystackError as e:
        logger.exception("Paystack verify failed")
        messages.error(request, "Could not verify payment.")
        return redirect('store:checkout')

    txn.raw_response = data
    if data.get('status') == 'success':
        txn.verified = True
        txn.save()
        order.mark_paid()
        return redirect('store:order_success', order_number=order.order_number)
    else:
        txn.save()
        order.status = Order.STATUS_FAILED
        order.save(update_fields=['status', 'updated_at'])
        messages.error(request, "Payment was not successful.")
        return redirect('store:checkout')
