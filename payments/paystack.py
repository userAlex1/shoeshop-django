"""
Paystack integration for card and bank payments.
Docs: https://paystack.com/docs/api/transaction/

Paystack supports Kenyan cards and M-Pesa too, but here we use it
specifically as the "card / bank" option, separate from our direct
Daraja STK Push integration.
"""
import requests
from django.conf import settings

BASE_URL = "https://api.paystack.co"


class PaystackError(Exception):
    pass


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def initialize_transaction(email, amount, reference, callback_url):
    """
    Start a transaction. Amount must be in the smallest currency unit
    (kobo for NGN, cents for KES -> so multiply KES by 100).
    Returns dict with an 'authorization_url' to redirect the customer to.
    """
    url = f"{BASE_URL}/transaction/initialize"
    payload = {
        "email": email,
        "amount": int(round(amount * 100)),
        "reference": reference,
        "callback_url": callback_url,
        "currency": "KES",
    }
    response = requests.post(url, json=payload, headers=_headers(), timeout=30)
    data = response.json()
    if not response.ok or not data.get('status'):
        raise PaystackError(f"Failed to initialize transaction: {data}")
    return data['data']


def verify_transaction(reference):
    """Verify a transaction after the customer returns from Paystack's checkout page."""
    url = f"{BASE_URL}/transaction/verify/{reference}"
    response = requests.get(url, headers=_headers(), timeout=30)
    data = response.json()
    if not response.ok or not data.get('status'):
        raise PaystackError(f"Failed to verify transaction: {data}")
    return data['data']
