from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Cart, Order
from app.cart.services import get_session_id

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("catalog.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        # Basic rate limiting counter per session
        failed_attempts = session.get("login_failed_attempts", 0)
        if failed_attempts >= 5:
            flash("Too many failed login attempts. Please wait a few minutes before trying again.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.pop("login_failed_attempts", None)
            login_user(user, remember=remember)

            # Reassign session cart to this user if they had items before logging in
            session_id = get_session_id()
            guest_cart = Cart.query.filter_by(session_id=session_id).first()
            user_cart = Cart.query.filter_by(user_id=user.id).first()

            if guest_cart and not user_cart:
                guest_cart.user_id = user.id
                db.session.commit()
            elif guest_cart and user_cart and guest_cart.id != user_cart.id:
                # Merge guest cart items into user cart
                for item in guest_cart.items:
                    existing = next((i for i in user_cart.items if i.book_id == item.book_id and i.variant_id == item.variant_id), None)
                    if existing:
                        existing.quantity = min(existing.quantity + item.quantity, 10)
                    else:
                        item.cart_id = user_cart.id
                db.session.delete(guest_cart)
                db.session.commit()

            flash(f"Welcome back, {user.name}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("catalog.home"))
        else:
            session["login_failed_attempts"] = failed_attempts + 1
            flash("Invalid email or password. Please try again.", "error")

    return render_template("auth/login.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("catalog.home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long for security.", "error")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("auth/register.html")

        user = User(name=name, email=email, phone=phone, address=address)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Link guest cart to new user
        session_id = get_session_id()
        guest_cart = Cart.query.filter_by(session_id=session_id).first()
        if guest_cart:
            guest_cart.user_id = user.id
            db.session.commit()

        login_user(user)
        flash(f"Welcome to bookish, {user.name}!", "success")
        return redirect(url_for("catalog.home"))

    return render_template("auth/register.html")

@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name:
            flash("Name cannot be empty.", "error")
        else:
            current_user.name = name
            current_user.phone = phone
            current_user.address = address
            db.session.commit()
            flash("Your profile details have been updated.", "success")
            return redirect(url_for("auth.account"))

    orders_count = Order.query.filter_by(user_id=current_user.id).count()
    recent_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(3).all()

    return render_template(
        "auth/account.html",
        orders_count=orders_count,
        recent_orders=recent_orders,
    )

@bp.post("/account/change-password")
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("Incorrect current password.", "error")
        return redirect(url_for("auth.account"))

    if len(new_password) < 8:
        flash("New password must be at least 8 characters long.", "error")
        return redirect(url_for("auth.account"))

    if new_password != confirm_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for("auth.account"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("Your password has been changed successfully.", "success")
    return redirect(url_for("auth.account"))

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("catalog.home"))
