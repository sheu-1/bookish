from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Book, BookVariant
from app.cart.services import (
    get_or_create_cart,
    cart_lines,
    cart_subtotal_kes,
    calculate_delivery_fee,
    clear_cart,
)

bp = Blueprint("cart", __name__, url_prefix="/cart")

@bp.get("")
def view():
    cart = get_or_create_cart()
    lines = cart_lines()
    subtotal = cart_subtotal_kes(lines)
    delivery = calculate_delivery_fee(subtotal)
    gift_fee = 150 if cart.is_gift else 0
    total = subtotal + (delivery if subtotal > 0 else 0) + (gift_fee if subtotal > 0 else 0)

    return render_template(
        "cart.html",
        cart=cart,
        lines=lines,
        subtotal=subtotal,
        delivery=delivery,
        gift_fee=gift_fee,
        total=total,
    )

@bp.post("/add")
def add():
    book_id = request.form.get("book_id", type=int)
    variant_id = request.form.get("variant_id", type=int) or None
    quantity = request.form.get("quantity", default=1, type=int)

    if quantity < 1:
        quantity = 1
    if quantity > 10:
        quantity = 10

    book = db.session.get(Book, book_id)
    if not book:
        abort(404)
    variant = None
    if variant_id:
        variant = BookVariant.query.filter_by(id=variant_id, book_id=book.id).first()

    cart = get_or_create_cart()

    # Check if item is already in cart
    item = None
    for ci in cart.items:
        if ci.book_id == book.id and ci.variant_id == (variant.id if variant else None):
            item = ci
            break

    if item:
        item.quantity = min(item.quantity + quantity, 10)
    else:
        from app.models import CartItem
        item = CartItem(
            cart_id=cart.id,
            book_id=book.id,
            variant_id=variant.id if variant else None,
            quantity=quantity,
        )
        db.session.add(item)

    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "success",
            "message": f"Added '{book.title}' to your bag!",
            "cart_count": cart.total_items,
        })

    flash(f"Added '{book.title}' to your bag!", "success")
    return redirect(request.referrer or url_for("cart.view"))

@bp.post("/update")
def update():
    item_id = request.form.get("item_id", type=int)
    quantity = request.form.get("quantity", type=int)
    cart = get_or_create_cart()

    for item in cart.items:
        if item.id == item_id:
            if quantity <= 0:
                db.session.delete(item)
            else:
                item.quantity = min(quantity, 10)
            break

    db.session.commit()
    return redirect(url_for("cart.view"))

@bp.post("/remove")
def remove():
    item_id = request.form.get("item_id", type=int)
    cart = get_or_create_cart()

    for item in cart.items:
        if item.id == item_id:
            db.session.delete(item)
            break

    db.session.commit()
    flash("Item removed from your cart.", "info")
    return redirect(url_for("cart.view"))

@bp.post("/gift")
def toggle_gift():
    cart = get_or_create_cart()
    cart.is_gift = request.form.get("is_gift") == "on"
    cart.gift_note = request.form.get("gift_note", "").strip() or None
    db.session.commit()
    return redirect(url_for("cart.view"))
