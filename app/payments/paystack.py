import hmac
import hashlib
import secrets
import logging
import requests
from flask import current_app, url_for

logger = logging.getLogger(__name__)

BASE = "https://api.paystack.co"

# In-memory store for mock transactions in dev/test mode
_MOCK_TRANSACTIONS = {}

def _headers():
    secret_key = current_app.config.get("PAYSTACK_SECRET_KEY", "")
    return {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

def new_reference(order_id: int) -> str:
    return f"BK-{order_id}-{secrets.token_hex(6)}"

def is_mock_mode() -> bool:
    key = current_app.config.get("PAYSTACK_SECRET_KEY", "")
    mock_flag = current_app.config.get("PAYSTACK_MOCK_ENABLED", False)
    # If explicitly in mock mode and using placeholder keys or in testing mode
    return (
        mock_flag
        and (not key or "placeholder" in key or key.startswith("mock_") or current_app.config.get("TESTING"))
    )

def initialize(email: str, amount_kes: int, reference: str, callback_url: str, metadata: dict):
    """
    Initializes a transaction with Paystack.
    amount_kes is converted to subunits (KES x 100).
    """
    if is_mock_mode():
        logger.info(f"Using Paystack sandbox mock for reference: {reference}")
        _MOCK_TRANSACTIONS[reference] = {
            "status": "pending",
            "amount": int(amount_kes * 100),
            "currency": "KES",
            "reference": reference,
            "customer": {"email": email},
            "metadata": metadata,
            "callback_url": callback_url,
            "id": secrets.randbelow(9000000) + 1000000,
            "channel": "card",
        }
        mock_auth_url = url_for("payments.mock_checkout", reference=reference, _external=True)
        return {
            "authorization_url": mock_auth_url,
            "access_code": f"mock_acc_{reference}",
            "reference": reference,
        }

    payload = {
        "email": email,
        "amount": int(amount_kes * 100),   # KES -> subunit
        "currency": "KES",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": metadata,
    }
    
    # Allow channels customization from config if provided
    channels = current_app.config.get("PAYSTACK_CHANNELS")
    if channels:
        payload["channels"] = channels

    logger.info(f"Calling Paystack API initialize for ref {reference}, amount KES {amount_kes}")
    try:
        r = requests.post(f"{BASE}/transaction/initialize",
                          json=payload, headers=_headers(), timeout=15)
        body = r.json()
    except requests.RequestException as e:
        logger.error(f"Paystack initialize network error: {e}")
        raise RuntimeError("Could not connect to payment gateway. Please try again.")

    if not body.get("status"):
        msg = body.get("message", "Paystack initialize failed")
        logger.error(f"Paystack initialize returned status false: {msg}")
        raise RuntimeError(msg)

    return body["data"]   # authorization_url, access_code, reference

def verify(reference: str):
    """
    Verifies transaction status directly from Paystack.
    """
    if is_mock_mode() and reference in _MOCK_TRANSACTIONS:
        tx = _MOCK_TRANSACTIONS[reference]
        return {
            "id": tx.get("id", 123456789),
            "status": tx.get("status", "success"),
            "reference": reference,
            "amount": tx.get("amount"),
            "currency": tx.get("currency", "KES"),
            "channel": tx.get("channel", "card"),
            "gateway_response": "Successful" if tx.get("status") == "success" else "Declined",
            "paid_at": "2026-11-25T12:00:00.000Z",
            "customer": tx.get("customer", {}),
        }

    logger.info(f"Calling Paystack API verify for ref {reference}")
    try:
        r = requests.get(f"{BASE}/transaction/verify/{reference}",
                         headers=_headers(), timeout=15)
        body = r.json()
    except requests.RequestException as e:
        logger.error(f"Paystack verify network error: {e}")
        raise RuntimeError("Payment verification request timed out.")

    if not body.get("status"):
        msg = body.get("message", "Paystack verify failed")
        logger.error(f"Paystack verify returned status false: {msg}")
        raise RuntimeError(msg)

    return body["data"]

def valid_signature(raw_body: bytes, signature: str) -> bool:
    """
    Verifies that incoming webhook requests are signed with HMAC-SHA512
    using PAYSTACK_SECRET_KEY.
    """
    if is_mock_mode() and signature == "mock_valid_signature":
        return True
    key = current_app.config.get("PAYSTACK_SECRET_KEY", "").encode("utf-8")
    if not key:
        return False
    expected = hmac.new(key, raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature or "")

def update_mock_status(reference: str, status: str, channel: str = "card"):
    if reference in _MOCK_TRANSACTIONS:
        _MOCK_TRANSACTIONS[reference]["status"] = status
        _MOCK_TRANSACTIONS[reference]["channel"] = channel
