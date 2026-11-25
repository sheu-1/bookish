import uuid
from flask import session
from flask_login import current_user
from app.extensions import db
from app.models import Cart, CartItem, Book, BookVariant

SESSION_CART_KEY = "bookish_cart_session"

def get_session_id() -> str:
    if SESSION_CART_KEY not in session:
        session[SESSION_CART_KEY] = str(uuid.uuid4())
    return session[SESSION_CART_KEY]

def get_or_create_cart() -> Cart:
    sess_id = get_session_id()
    cart = None
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            # Check if there is an existing guest cart with this session
            cart = Cart.query.filter_by(session_id=sess_id).first()
            if cart:
                cart.user_id = current_user.id
                db.session.commit()
    else:
        cart = Cart.query.filter_by(session_id=sess_id).first()

    if not cart:
        cart = Cart(
            session_id=sess_id,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(cart)
        db.session.commit()

    return cart

class CartLineItem:
    def __init__(self, item: CartItem):
        self.id = item.id
        self.book = item.book
        self.variant = item.variant
        self.qty = item.quantity
        self.quantity = item.quantity
        self.unit_price = item.unit_price_kes
        self.unit_price_kes = item.unit_price_kes
        self.line_total = item.line_total_kes
        self.line_total_kes = item.line_total_kes
        self.format_name = item.format_name

def cart_lines():
    cart = get_or_create_cart()
    return [CartLineItem(i) for i in cart.items]

def cart_items_count() -> int:
    cart = get_or_create_cart()
    return cart.total_items

def cart_subtotal_kes(lines=None) -> int:
    if lines is None:
        lines = cart_lines()
    return sum(l.line_total_kes for l in lines)

def calculate_delivery_fee(subtotal_kes: int) -> int:
    # Free standard delivery over KES 2,500, otherwise flat KES 200
    if subtotal_kes >= 2500 or subtotal_kes == 0:
        return 0
    return 200

def cart_total_kes(lines=None, is_gift=False) -> int:
    subtotal = cart_subtotal_kes(lines)
    if subtotal == 0:
        return 0
    delivery = calculate_delivery_fee(subtotal)
    gift_fee = 150 if is_gift else 0
    return subtotal + delivery + gift_fee

def clear_cart():
    cart = get_or_create_cart()
    for item in list(cart.items):
        db.session.delete(item)
    cart.is_gift = False
    cart.gift_note = None
    db.session.commit()
