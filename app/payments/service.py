from datetime import datetime, timezone
from app.extensions import db
from app.models import Order, Payment, Book
from app.payments import paystack
from app.cart.services import clear_cart

def verify_and_complete(reference: str) -> str:
    """Returns 'paid', 'failed' or 'unknown'. Safe to call many times."""
    # SQLite doesn't support with_for_update(), but Postgres does. Use query cleanly:
    query = Order.query.filter_by(reference=reference)
    try:
        order = query.with_for_update().first()
    except Exception:
        order = query.first()

    if order is None:
        return "unknown"
    if order.status == "paid":
        return "paid"  # already done (callback + webhook race)

    try:
        data = paystack.verify(reference)
    except Exception as e:
        # If API failed, keep order pending for retry or webhook
        return "unknown"

    ok = (
        data.get("status") == "success"
        and data.get("currency") == "KES"
        and int(data.get("amount", 0)) == order.total_kes * 100
        and data.get("reference") == order.reference
    )
    if not ok:
        if data.get("status") in ("failed", "abandoned"):
            order.status = "payment_failed"
            db.session.commit()
            return "failed"
        return "failed"

    # confirmed -> now log it, in one transaction
    db.session.add(
        Payment(
            order_id=order.id,
            provider="paystack",
            reference=reference,
            provider_transaction_id=str(data.get("id")),
            channel=data.get("channel", "card"),
            amount_kes=order.total_kes,
            currency="KES",
            status="success",
            paid_at=datetime.now(timezone.utc),
            raw_response=data,  # JSON column, keep for audits
        )
    )
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)

    # Decrement stock for each item
    for item in order.items:
        if item.variant:
            item.variant.stock = max(0, item.variant.stock - item.quantity)
        if item.book:
            item.book.stock = max(0, item.book.stock - item.quantity)

    db.session.commit()
    return "paid"
