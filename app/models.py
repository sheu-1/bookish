from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    orders = db.relationship("Order", back_populates="user", lazy=True, order_by="desc(Order.created_at)")
    carts = db.relationship("Cart", back_populates="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    colour_token = db.Column(db.String(50), default="violet", nullable=False)  # violet, sunshine, pink, mint

    books = db.relationship("Book", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)

    price_kes = db.Column(db.Integer, nullable=False)  # Whole KES shillings
    stock = db.Column(db.Integer, default=10, nullable=False)

    cover_image = db.Column(db.String(500), nullable=True)
    cover_bg = db.Column(db.String(50), default="#6C3BFF", nullable=False)
    cover_fg = db.Column(db.String(50), default="#FFFFFF", nullable=False)
    cover_accent = db.Column(db.String(50), default="#FFD23F", nullable=False)
    cover_shape = db.Column(db.String(50), default="circle", nullable=False)  # circle, arch, rounded_square, leaf

    tag = db.Column(db.String(50), nullable=True)  # New / Bestseller / Staff pick / Kids favourite
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    category = db.relationship("Category", back_populates="books")
    variants = db.relationship("BookVariant", back_populates="book", cascade="all, delete-orphan", lazy=True)

    def default_variant(self):
        if self.variants:
            return self.variants[0]
        return None

    def __repr__(self):
        return f"<Book {self.title}>"


class BookVariant(db.Model):
    __tablename__ = "book_variants"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    format = db.Column(db.String(50), nullable=False)  # Paperback, Hardcover, eBook
    price_kes = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=10, nullable=False)

    book = db.relationship("Book", back_populates="variants")

    def __repr__(self):
        return f"<BookVariant {self.format} - {self.book_id}>"


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    is_gift = db.Column(db.Boolean, default=False, nullable=False)
    gift_note = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = db.relationship("User", back_populates="carts")
    items = db.relationship("CartItem", back_populates="cart", cascade="all, delete-orphan", lazy=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)

    @property
    def subtotal_kes(self):
        return sum(item.line_total_kes for item in self.items)


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("book_variants.id"), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    cart = db.relationship("Cart", back_populates="items")
    book = db.relationship("Book")
    variant = db.relationship("BookVariant")

    @property
    def unit_price_kes(self):
        if self.variant:
            return self.variant.price_kes
        return self.book.price_kes

    @property
    def line_total_kes(self):
        return self.unit_price_kes * self.quantity

    @property
    def format_name(self):
        return self.variant.format if self.variant else "Standard"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    status = db.Column(
        db.String(50), default="pending", nullable=False
    )  # pending | paid | payment_failed | shipped | delivered | cancelled
    total_kes = db.Column(db.Integer, nullable=False)
    delivery_name = db.Column(db.String(120), nullable=True)
    delivery_phone = db.Column(db.String(50), nullable=True)
    delivery_email = db.Column(db.String(255), nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    delivery_notes = db.Column(db.Text, nullable=True)
    delivery_fee_kes = db.Column(db.Integer, default=0, nullable=False)
    is_gift = db.Column(db.Boolean, default=False, nullable=False)
    gift_note = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    paid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy=True)
    payment = db.relationship("Payment", back_populates="order", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Order {self.reference} ({self.status})>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("book_variants.id"), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price_kes = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    book = db.relationship("Book")
    variant = db.relationship("BookVariant")

    @property
    def line_total_kes(self):
        return self.unit_price_kes * self.quantity

    @property
    def format_name(self):
        return self.variant.format if self.variant else "Standard"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    provider = db.Column(db.String(50), default="paystack", nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    provider_transaction_id = db.Column(db.String(100), nullable=True)
    channel = db.Column(db.String(50), nullable=True)
    amount_kes = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default="KES", nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'success'
    paid_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    raw_response = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    order = db.relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment {self.reference} - {self.status}>"


class WebhookEvent(db.Model):
    __tablename__ = "webhook_events"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    payload = db.Column(db.JSON, nullable=True)
    received_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @classmethod
    def seen(cls, reference: str) -> bool:
        if not reference:
            return False
        return cls.query.filter_by(reference=reference).first() is not None

    @classmethod
    def record(cls, reference: str, payload: dict):
        event = cls(reference=reference, payload=payload)
        db.session.add(event)
        db.session.commit()
        return event


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
