"""
Safaricom Daraja API client (STK Push / Lipa na M-Pesa Online).

Docs: https://developer.safaricom.co.ke/APIs/MpesaExpressSimulate

Flow:
1. get_access_token()   -> OAuth token using consumer key/secret
2. stk_push(...)        -> triggers the STK prompt on the customer's phone
3. Safaricom calls MPESA_CALLBACK_URL with the result (see payments/views.py)
"""
import base64
import requests
from django.conf import settings
from django.utils import timezone

SANDBOX_BASE_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE_URL = "https://api.safaricom.co.ke"


def get_base_url():
    return PRODUCTION_BASE_URL if settings.MPESA_ENV == 'production' else SANDBOX_BASE_URL


class MpesaError(Exception):
    pass


def get_access_token():
    """Fetch an OAuth access token using the consumer key/secret."""
    url = f"{get_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=30,
    )
    if response.status_code != 200:
        raise MpesaError(f"Failed to get access token: {response.status_code} {response.text}")
    return response.json()['access_token']


def _generate_password_and_timestamp():
    timestamp = timezone.localtime(timezone.now()).strftime('%Y%m%d%H%M%S')
    raw_password = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw_password.encode()).decode()
    return password, timestamp


def format_phone_number(phone):
    """Normalize to 2547XXXXXXXX / 2541XXXXXXXX format required by Daraja."""
    phone = phone.strip().replace(' ', '').replace('+', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone
    return phone


def stk_push(phone_number, amount, order_number, description="Shoe order payment"):
    """
    Trigger an STK push prompt on the customer's phone.
    Returns the parsed JSON response from Safaricom, which includes
    MerchantRequestID and CheckoutRequestID needed to match the callback.
    """
    access_token = get_access_token()
    password, timestamp = _generate_password_and_timestamp()
    phone_number = format_phone_number(phone_number)

    url = f"{get_base_url()}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(round(amount)),  # Daraja sandbox requires whole numbers
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": str(order_number)[:12],
        "TransactionDesc": description,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()
    if response.status_code != 200:
        raise MpesaError(f"STK push failed: {data}")
    return data


def query_stk_status(checkout_request_id):
    """Optional: poll Safaricom for the status of an STK push (if callback is delayed)."""
    access_token = get_access_token()
    password, timestamp = _generate_password_and_timestamp()
    url = f"{get_base_url()}/mpesa/stkpushquery/v1/query"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    return response.json()
