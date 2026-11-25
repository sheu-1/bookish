from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Order

bp = Blueprint("orders", __name__, url_prefix="/orders")

@bp.get("")
def list_orders():
    if current_user.is_authenticated:
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        return render_template("orders/list.html", orders=orders)

    # Guest lookup by reference
    ref = request.args.get("ref", "").strip()
    if ref:
        order = Order.query.filter_by(reference=ref).first()
        if order:
            return redirect(url_for("orders.detail", reference=ref))
        flash("Order not found with that reference.", "error")

    return render_template("orders/lookup.html")

@bp.get("/<reference>")
def detail(reference):
    order = Order.query.filter_by(reference=reference).first_or_404()
    # Protect if order belongs to a user and current user is a different logged-in user
    if order.user_id and current_user.is_authenticated and order.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    return render_template("orders/detail.html", order=order)
