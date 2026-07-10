import requests
import base64
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_callback_url(callback_url):
    """Ensure M-Pesa uses the correct payment callback endpoint."""
    if not callback_url:
        return callback_url

    callback_url = callback_url.strip().rstrip('/')

    if callback_url.endswith('/api/mpesa/callback'):
        return callback_url.replace('/api/mpesa/callback', '/api/payments/mpesa/callback') + '/'

    if callback_url.endswith('/mpesa/callback'):
        return callback_url.replace('/mpesa/callback', '/api/payments/mpesa/callback') + '/'

    return callback_url + '/api/payments/mpesa/callback/'


def get_mpesa_token():
    """Get OAuth access token from Safaricom"""
    consumer_key    = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    credentials = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode()

    response = requests.get(
        'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials',
        headers={'Authorization': f'Basic {credentials}'},
        timeout=15,
    )

    if response.status_code != 200:
        logger.error(
            "MPESA token request failed: %s %s", response.status_code, response.text
        )
        return None

    token = response.json().get('access_token')
    if not token:
        logger.error("MPESA token response missing access_token: %s", response.text)
    return token


def normalize_phone_number(phone_number):
    """
    Normalize a Kenyan phone number to the 2547XXXXXXXX / 2541XXXXXXXX
    format required by Daraja, regardless of how the user typed it.
    Handles: 07XXXXXXXX, 01XXXXXXXX, 7XXXXXXXX, 1XXXXXXXX,
             254XXXXXXXXX, +254XXXXXXXXX, and inputs with spaces/dashes.
    """
    phone_number = str(phone_number).strip().replace(" ", "").replace("-", "")

    if phone_number.startswith('+'):
        phone_number = phone_number[1:]
    elif phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('7') or phone_number.startswith('1'):
        phone_number = '254' + phone_number

    return phone_number


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
    token = get_mpesa_token()
    if not token:
        return {
            'ResponseCode': '1',
            'errorMessage': 'Could not authenticate with M-Pesa (check consumer key/secret).',
        }

    password, timestamp = generate_password()
    phone_number = normalize_phone_number(phone_number)
    callback_url = normalize_callback_url(settings.MPESA_CALLBACK_URL)

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": f"EventHub-{booking_id}",
        "TransactionDesc": f"Payment for booking {booking_id}"
    }

    logger.info(
        "Initiating STK push: phone=%s amount=%s booking_id=%s callback=%s",
        phone_number, amount, booking_id, callback_url,
    )

    try:
        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=20,
        )
    except requests.exceptions.RequestException as exc:
        logger.error("STK push request failed to reach Safaricom: %s", exc)
        return {
            'ResponseCode': '1',
            'errorMessage': f'Could not reach Safaricom: {exc}',
        }

    data = response.json()
    logger.info("STK push response: %s", data)
    return data