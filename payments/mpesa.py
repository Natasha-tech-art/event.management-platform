import requests
import base64
from datetime import datetime
from django.conf import settings


def get_mpesa_token():
    """Get OAuth access token from Safaricom"""
    consumer_key    = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    credentials = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode()

    response = requests.get(
        'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        headers={'Authorization': f'Basic {credentials}'}
    )
    return response.json().get('access_token')


def generate_password():
    """Generate M-Pesa password"""
    shortcode  = settings.MPESA_SHORTCODE
    passkey    = settings.MPESA_PASSKEY
    timestamp  = datetime.now().strftime('%Y%m%d%H%M%S')
    raw        = f"{shortcode}{passkey}{timestamp}"
    password   = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(phone_number, amount, booking_id):
    """Initiate STK Push to customer's phone"""
    token     = get_mpesa_token()
    password, timestamp = generate_password()

    # Format phone number (must start with 254)
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"EventHub-{booking_id}",
        "TransactionDesc": f"Payment for booking {booking_id}"
    }

    response = requests.post(
        'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
        json=payload,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    return response.json()