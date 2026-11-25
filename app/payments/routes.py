from flask import Blueprint, request, redirect, url_for, render_template, abort, current_app, flash, session
from flask_login import current_user
from app.cart.services import cart_lines, cart_subtotal_kes, calculate_delivery_fee, clear_cart, get_or_create_cart
from app.extensions import db, csrf
from app.models import Order, OrderItem, WebhookEvent
from app.payments import paystack
from app.payments.service import verify_and_complete

bp = Blueprint("payments", __name__)

@bp.route("/checkout/details", methods=["GET", "POST"])
def checkout_details():
    lines = cart_lines()
    if not lines:
        flash("Your cart is empty. Add some books first!", "info")
        return redirect(url_for("cart.view"))

    cart = get_or_create_cart()
    subtotal = cart_subtotal_kes(lines)
    delivery = calculate_delivery_fee(subtotal)
    gift_fee = 150 if cart.is_gift else 0
    total = subtotal + delivery + gift_fee

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        notes = request.form.get("notes", "").strip()

        if not name or not email or not phone or not address:
            flash("Please fill in all required delivery fields.", "error")
            return render_template(
                "checkout_details.html",
                lines=lines,
                subtotal=subtotal,
                delivery=delivery,
                gift_fee=gift_fee,
                total=total,
                form_data=request.form,
            )

        # Store delivery info in session for payment init
        session["checkout_delivery"] = {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "notes": notes,
        }
        return redirect(url_for("payments.checkout_summary"))

    # Prefill from current_user if logged in or session
    form_data = session.get("checkout_delivery", {})
    if current_user.is_authenticated and not form_data:
        form_data = {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone or "",
        }

    return render_template(
        "checkout_details.html",
        lines=lines,
        subtotal=subtotal,
        delivery=delivery,
        gift_fee=gift_fee,
        total=total,
        form_data=form_data,
    )

@bp.get("/checkout/summary")
def checkout_summary():
    lines = cart_lines()
    if not lines:
        return redirect(url_for("cart.view"))

    delivery_info = session.get("checkout_delivery")
    if not delivery_info:
        return redirect(url_for("payments.checkout_details"))

    cart = get_or_create_cart()
    subtotal = cart_subtotal_kes(lines)
    delivery = calculate_delivery_fee(subtotal)
    gift_fee = 150 if cart.is_gift else 0
    total = subtotal + delivery + gift_fee

    return render_template(
        "checkout_summary.html",
        lines=lines,
        delivery_info=delivery_info,
        cart=cart,
        subtotal=subtotal,
        delivery=delivery,
        gift_fee=gift_fee,
        total=total,
    )

@bp.post("/checkout/pay")
def pay():
    lines = cart_lines()
    if not lines:
        return redirect(url_for("cart.view"))

    delivery_info = session.get("checkout_delivery", {})
    email = delivery_info.get("email") or (current_user.email if current_user.is_authenticated else request.form.get("email"))

    if not email:
        flash("An email is required for payment confirmation.", "error")
        return redirect(url_for("payments.checkout_details"))

    cart = get_or_create_cart()
    subtotal = cart_subtotal_kes(lines)
    delivery_fee = calculate_delivery_fee(subtotal)
    gift_fee = 150 if cart.is_gift else 0
    total_kes = subtotal + delivery_fee + gift_fee

    # Create order with status = "pending"
    order = Order(
        user_id=current_user.id if current_user.is_authenticated else None,
        status="pending",
        total_kes=total_kes,
        delivery_name=delivery_info.get("name", "Customer"),
        delivery_email=email,
        delivery_phone=delivery_info.get("phone", ""),
        delivery_address=delivery_info.get("address", ""),
        delivery_notes=delivery_info.get("notes", ""),
        delivery_fee_kes=delivery_fee,
        is_gift=cart.is_gift,
        gift_note=cart.gift_note,
        reference="",  # will be set after flush
    )
    db.session.add(order)
    db.session.flush()

    for l in lines:
        db.session.add(
            OrderItem(
                order_id=order.id,
                book_id=l.book.id,
                variant_id=l.variant.id if l.variant else None,
                quantity=l.qty,
                unit_price_kes=l.unit_price,
            )
        )

    order.reference = paystack.new_reference(order.id)
    db.session.commit()

    callback_url = url_for("payments.callback", _external=True)

    try:
        data = paystack.initialize(
            email=email,
            amount_kes=order.total_kes,
            reference=order.reference,
            callback_url=callback_url,
            metadata={"order_id": order.id, "email": email},
        )
        return redirect(data["authorization_url"])
    except Exception as e:
        current_app.logger.error(f"Paystack initialize error: {e}")
        flash(f"Payment initiation failed: {str(e)}", "error")
        return redirect(url_for("payments.checkout_summary"))

@bp.get("/payment/callback")
def callback():
    reference = request.args.get("reference") or request.args.get("trxref")
    if not reference:
        abort(400)

    result = verify_and_complete(reference)
    order = Order.query.filter_by(reference=reference).first()

    if result == "paid":
        clear_cart()
        # Clear checkout delivery session
        session.pop("checkout_delivery", None)
        return render_template("payment_success.html", reference=reference, order=order)

    return render_template("payment_failed.html", reference=reference, order=order)

@bp.post("/webhooks/paystack")
@csrf.exempt
def webhook():
    raw = request.get_data()
    sig = request.headers.get("x-paystack-signature")
    if not paystack.valid_signature(raw, sig):
        abort(401)

    event = request.get_json(silent=True) or {}
    if event.get("event") == "charge.success":
        data = event.get("data", {})
        ref = data.get("reference")
        if ref and not WebhookEvent.seen(ref):
            WebhookEvent.record(ref, event)
            verify_and_complete(ref)

    return "", 200

# Mock checkout route for local testing / demo
@bp.route("/payments/mock-paystack/<reference>", methods=["GET", "POST"])
def mock_checkout(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()

    if request.method == "POST":
        action = request.form.get("action")
        channel = request.form.get("channel", "card")

        if action == "pay":
            paystack.update_mock_status(reference, "success", channel=channel)
            return redirect(url_for("payments.callback", reference=reference))
        elif action == "fail":
            paystack.update_mock_status(reference, "failed", channel=channel)
            return redirect(url_for("payments.callback", reference=reference))
        else:
            paystack.update_mock_status(reference, "abandoned", channel=channel)
            return redirect(url_for("payments.callback", reference=reference))

    return render_template("mock_paystack.html", order=order, reference=reference)
