from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book, Order, User, Category

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.before_request
@login_required
def admin_required():
    if not current_user.is_admin:
        abort(403)

@bp.get("")
def dashboard():
    total_orders = Order.query.count()
    paid_orders = Order.query.filter_by(status="paid").count()
    total_revenue = db.session.query(db.func.sum(Order.total_kes)).filter_by(status="paid").scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    books = Book.query.order_by(Book.created_at.desc()).all()
    users_count = User.query.count()

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        paid_orders=paid_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        books=books,
        users_count=users_count,
    )

@bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    new_status = request.form.get("status")
    allowed = ["pending", "paid", "payment_failed", "shipped", "delivered", "cancelled"]
    if new_status in allowed:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} status updated to {new_status}.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.post("/books/<int:book_id>/stock")
def update_stock(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)
    new_stock = request.form.get("stock", type=int)
    if new_stock is not None and new_stock >= 0:
        book.stock = new_stock
        db.session.commit()
        flash(f"Stock for '{book.title}' updated to {new_stock}.", "success")
    return redirect(url_for("admin.dashboard"))
