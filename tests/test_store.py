import hmac
import hashlib
import json
import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import User, Category, Book, BookVariant, Order, Payment, WebhookEvent
from app.seeds import seed_data
from app.payments import paystack

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_data()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Find your next" in response.data
    assert b"Fresh off the shelf" in response.data
    assert b"Shop by shelf" in response.data
    assert b"Bundle deal" in response.data

def test_shop_catalog_and_filtering(client):
    # All books
    res = client.get("/shop")
    assert res.status_code == 200
    assert b"The shop" in res.data
    assert b"Tomorrow, and Tomorrow, and Tomorrow" in res.data

    # Filter by genre fiction
    res_fic = client.get("/shop?genre=fiction")
    assert res_fic.status_code == 200
    assert b"Tomorrow, and Tomorrow, and Tomorrow" in res_fic.data

    # Filter by search query
    res_search = client.get("/shop?q=Habits")
    assert res_search.status_code == 200
    assert b"Atomic Habits" in res_search.data
    assert b"Where the Wild Things Are" not in res_search.data

    # Sort price high to low
    res_sort = client.get("/shop?sort=price_high")
    assert res_sort.status_code == 200

def test_product_detail(client):
    res = client.get("/book/atomic-habits")
    assert res.status_code == 200
    assert b"Atomic Habits" in res.data
    assert b"James Clear" in res.data
    assert b"Paperback" in res.data
    assert b"Hardcover" in res.data

def test_cart_workflow(client):
    book = Book.query.filter_by(slug="atomic-habits").first()
    variant = book.variants[0]

    # 1. Add to cart
    res = client.post("/cart/add", data={
        "book_id": book.id,
        "variant_id": variant.id,
        "quantity": 2,
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Atomic Habits" in res.data
    assert b"Your cart" in res.data

    # 2. View cart
    res = client.get("/cart")
    assert res.status_code == 200
    assert b"Atomic Habits" in res.data

    # 3. Toggle gift wrap
    res = client.post("/cart/gift", data={
        "is_gift": "on",
        "gift_note": "Happy reading!",
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Happy reading!" in res.data

def test_user_registration_and_login(client):
    # Register
    res = client.post("/register", data={
        "name": "Alex Omondi",
        "email": "alex@example.com",
        "phone": "+254700112233",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome to bookish, Alex Omondi!" in res.data

    # Logout
    res = client.post("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"You have been signed out." in res.data

    # Login
    res = client.post("/login", data={
        "email": "alex@example.com",
        "password": "password123",
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, Alex Omondi!" in res.data

def test_paystack_payment_flow_and_idempotency(client, app):
    # 1. Add item to cart
    book = Book.query.filter_by(slug="tomorrow-and-tomorrow-and-tomorrow").first()
    initial_stock = book.stock
    client.post("/cart/add", data={"book_id": book.id, "quantity": 1})

    # 2. Enter delivery details
    client.post("/checkout/details", data={
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+254712345678",
        "address": "Kilimani, Nairobi",
        "notes": "Call upon arrival",
    }, follow_redirects=True)

    # 3. Pay via Paystack
    res = client.post("/checkout/pay")
    # Redirects to authorization URL
    assert res.status_code == 302
    assert "mock-paystack" in res.headers["Location"] or "checkout" in res.headers["Location"]

    order = Order.query.order_by(Order.id.desc()).first()
    assert order.status == "pending"
    assert order.reference.startswith(f"BK-{order.id}-")

    # 4. Simulate mock authorization
    client.post(f"/payments/mock-paystack/{order.reference}", data={
        "action": "pay",
        "channel": "mobile_money",
    })

    # 5. Callback verification
    res_cb = client.get(f"/payment/callback?reference={order.reference}")
    assert res_cb.status_code == 200
    assert b"Thank you for your order!" in res_cb.data

    db.session.refresh(order)
    assert order.status == "paid"
    assert order.paid_at is not None

    # Check payment row was logged
    payment = Payment.query.filter_by(order_id=order.id).first()
    assert payment is not None
    assert payment.status == "success"
    assert payment.channel == "mobile_money"
    assert payment.amount_kes == order.total_kes

    # Check stock was decremented
    db.session.refresh(book)
    assert book.stock == initial_stock - 1

    # 6. Idempotency check: Call verify_and_complete again with the same reference
    from app.payments.service import verify_and_complete
    status = verify_and_complete(order.reference)
    assert status == "paid"
    # Ensure payments table doesn't get duplicate row
    assert Payment.query.filter_by(order_id=order.id).count() == 1
    # Stock not decremented again
    db.session.refresh(book)
    assert book.stock == initial_stock - 1

def test_paystack_webhook_signature_and_event(client, app):
    # Setup pending order
    book = Book.query.first()
    order = Order(
        user_id=None,
        reference="BK-WEBHOOK-12345",
        status="pending",
        total_kes=book.price_kes,
        delivery_name="Webhook Tester",
        delivery_email="test@webhook.org",
        delivery_phone="+254700000000",
        delivery_address="Nairobi",
    )
    db.session.add(order)
    db.session.commit()

    # Preload mock transaction data for verification
    paystack._MOCK_TRANSACTIONS[order.reference] = {
        "status": "success",
        "amount": order.total_kes * 100,
        "currency": "KES",
        "reference": order.reference,
        "id": 999999,
        "channel": "card",
    }

    payload = json.dumps({
        "event": "charge.success",
        "data": {
            "reference": order.reference,
            "status": "success",
            "amount": order.total_kes * 100,
            "currency": "KES",
        }
    }).encode("utf-8")

    # 1. Invalid signature should return 401
    bad_res = client.post("/webhooks/paystack", data=payload, headers={
        "Content-Type": "application/json",
        "x-paystack-signature": "invalid_signature",
    })
    assert bad_res.status_code == 401

    # 2. Valid signature using HMAC-SHA512
    key = app.config["PAYSTACK_SECRET_KEY"].encode("utf-8")
    valid_sig = hmac.new(key, payload, hashlib.sha512).hexdigest()

    ok_res = client.post("/webhooks/paystack", data=payload, headers={
        "Content-Type": "application/json",
        "x-paystack-signature": valid_sig,
    })
    assert ok_res.status_code == 200

    db.session.refresh(order)
    assert order.status == "paid"
    assert WebhookEvent.seen(order.reference) is True

    # 3. Duplicate webhook event should be ignored idempotently
    dup_res = client.post("/webhooks/paystack", data=payload, headers={
        "Content-Type": "application/json",
        "x-paystack-signature": valid_sig,
    })
    assert dup_res.status_code == 200

def test_admin_dashboard_and_controls(client):
    # Sign in as admin
    client.post("/login", data={
        "email": "admin@bookish.co",
        "password": "admin123",
    })

    res = client.get("/admin")
    assert res.status_code == 200
    assert b"Admin Dashboard" in res.data
    assert b"Store Operations" in res.data

def test_user_account_management(client):
    # Sign in as customer
    client.post("/login", data={
        "email": "jane@example.com",
        "password": "secret123",
    })

    # Access account profile
    res = client.get("/account")
    assert res.status_code == 200
    assert b"My Account" in res.data
    assert b"Personal Details" in res.data

    # Update profile details
    res_update = client.post("/account", data={
        "name": "Jane Mwangi Updated",
        "phone": "+254799888777",
        "address": "Riverside Drive, Nairobi",
    }, follow_redirects=True)
    assert res_update.status_code == 200
    assert b"Your profile details have been updated" in res_update.data

    user = User.query.filter_by(email="jane@example.com").first()
    assert user.name == "Jane Mwangi Updated"
    assert user.address == "Riverside Drive, Nairobi"

    # Change password
    res_pw = client.post("/account/change-password", data={
        "current_password": "secret123",
        "new_password": "brandnewpassword456",
        "confirm_password": "brandnewpassword456",
    }, follow_redirects=True)
    assert res_pw.status_code == 200
    assert b"Your password has been changed successfully" in res_pw.data
    assert user.check_password("brandnewpassword456") is True

def test_custom_404_error_page(client):
    res = client.get("/non-existent-page-url-xyz")
    assert res.status_code == 404
    assert b"Page not found" in res.data
    assert b"404 Error" in res.data

def test_payment_failure_flow(client):
    book = Book.query.first()
    client.post("/cart/add", data={"book_id": book.id, "quantity": 1})
    client.post("/checkout/details", data={
        "name": "Failed Payment Tester",
        "email": "fail@example.com",
        "phone": "+254711223344",
        "address": "Mombasa Road",
    })
    client.post("/checkout/pay")
    order = Order.query.order_by(Order.id.desc()).first()

    # Simulate payment failure in mock Paystack
    client.post(f"/payments/mock-paystack/{order.reference}", data={
        "action": "fail",
        "channel": "card",
    })

    res = client.get(f"/payment/callback?reference={order.reference}")
    assert res.status_code == 200
    assert b"Payment was not completed" in res.data
    db.session.refresh(order)
    assert order.status == "payment_failed"

def test_newsletter_subscription(client):
    res = client.post("/newsletter", data={"email": "reader@example.com"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"on the list" in res.data

    # Duplicate should not crash
    res_dup = client.post("/newsletter", data={"email": "reader@example.com"}, follow_redirects=True)
    assert res_dup.status_code == 200

