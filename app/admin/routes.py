import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Book, BookVariant, Order, User, Category

bp = Blueprint("admin", __name__, url_prefix="/admin")

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)

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
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(15).all()
    books = Book.query.order_by(Book.created_at.desc()).all()
    categories = Category.query.all()
    users_count = User.query.count()

    return render_template(
        "admin/dashboard.html",
        total_orders=total_orders,
        paid_orders=paid_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        books=books,
        categories=categories,
        users_count=users_count,
    )

@bp.route("/books/new", methods=["GET", "POST"])
def new_book():
    categories = Category.query.all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category_id = request.form.get("category_id", type=int)
        price_kes = request.form.get("price_kes", type=int)
        stock = request.form.get("stock", 10, type=int)
        description = request.form.get("description", "").strip()
        cover_image = request.form.get("cover_image", "").strip()
        tag = request.form.get("tag", "").strip() or None
        cover_bg = request.form.get("cover_bg", "#6C3BFF").strip()
        cover_shape = request.form.get("cover_shape", "circle").strip()

        if not title or not author or not category_id or not price_kes:
            flash("Please fill in Title, Author, Category, and Price.", "error")
            return render_template("admin/book_form.html", categories=categories, book=None)

        # Generate unique slug
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while Book.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        book = Book(
            title=title,
            slug=slug,
            author=author,
            category_id=category_id,
            price_kes=price_kes,
            stock=stock,
            description=description,
            cover_image=cover_image or None,
            tag=tag,
            cover_bg=cover_bg,
            cover_shape=cover_shape,
            is_active=True,
        )
        db.session.add(book)
        db.session.flush()

        # Optional formats: only add if admin explicitly checked/entered them
        selected_formats = request.form.getlist("formats")
        for fmt in selected_formats:
            fmt_name = fmt.strip()
            if fmt_name:
                fmt_price = request.form.get(f"price_{fmt_name}", type=int) or price_kes
                variant = BookVariant(
                    book_id=book.id,
                    format=fmt_name,
                    price_kes=fmt_price,
                    stock=stock,
                )
                db.session.add(variant)

        db.session.commit()

        flash(f"Book '{book.title}' created successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/book_form.html", categories=categories, book=None)

@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    categories = Category.query.all()
    if request.method == "POST":
        book.title = request.form.get("title", "").strip()
        book.author = request.form.get("author", "").strip()
        book.category_id = request.form.get("category_id", type=int)
        book.price_kes = request.form.get("price_kes", type=int)
        book.stock = request.form.get("stock", type=int)
        book.description = request.form.get("description", "").strip()
        book.cover_image = request.form.get("cover_image", "").strip() or None
        book.tag = request.form.get("tag", "").strip() or None
        book.cover_bg = request.form.get("cover_bg", "#6C3BFF").strip()
        book.cover_shape = request.form.get("cover_shape", "circle").strip()
        book.is_active = request.form.get("is_active") == "on"

        # Optional formats update
        if "formats_submitted" in request.form:
            selected_formats = [f.strip() for f in request.form.getlist("formats") if f.strip()]
            existing_by_fmt = {v.format: v for v in book.variants}
            # Remove unchecked formats
            for fmt, var in list(existing_by_fmt.items()):
                if fmt not in selected_formats:
                    db.session.delete(var)
            # Add or update checked formats
            for fmt in selected_formats:
                fmt_price = request.form.get(f"price_{fmt}", type=int) or book.price_kes
                if fmt in existing_by_fmt:
                    existing_by_fmt[fmt].price_kes = fmt_price
                else:
                    db.session.add(BookVariant(
                        book_id=book.id,
                        format=fmt,
                        price_kes=fmt_price,
                        stock=book.stock,
                    ))

        db.session.commit()
        flash(f"Book '{book.title}' updated successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/book_form.html", categories=categories, book=book)

@bp.post("/books/<int:book_id>/delete")
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)
    title = book.title
    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{title}' was deleted from the store.", "info")
    return redirect(url_for("admin.dashboard"))

@bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    new_status = request.form.get("status")
    allowed = ["pending", "paid", "payment_failed", "shipped", "delivered", "cancelled"]
    if new_status in allowed and new_status != order.status:
        # If moving from paid to cancelled, restore the stock
        if order.status in ("paid", "shipped", "delivered") and new_status in ("cancelled", "payment_failed"):
            for item in order.items:
                if item.variant:
                    item.variant.stock += item.quantity
                if item.book:
                    item.book.stock += item.quantity
        # If moving manually to paid, deduct stock
        elif order.status not in ("paid", "shipped", "delivered") and new_status == "paid":
            for item in order.items:
                if item.variant:
                    item.variant.stock = max(0, item.variant.stock - item.quantity)
                if item.book:
                    item.book.stock = max(0, item.book.stock - item.quantity)

        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} status updated to '{new_status}'.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.post("/books/<int:book_id>/stock")
def update_stock(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    add_stock = request.form.get("add_stock", type=int)
    new_stock = request.form.get("stock", type=int)

    if add_stock is not None and add_stock > 0:
        book.stock += add_stock
        if book.variants:
            for v in book.variants:
                v.stock += add_stock
        msg = f"Restocked: Added {add_stock} units to '{book.title}'. Total stock: {book.stock}."
    elif new_stock is not None and new_stock >= 0:
        book.stock = new_stock
        if book.variants:
            for v in book.variants:
                v.stock = new_stock
        msg = f"Stock for '{book.title}' set to {new_stock}."
    else:
        msg = "No stock changes made."

    if book.stock > 0:
        book.is_active = True

    db.session.commit()
    flash(msg, "success")
    return redirect(url_for("admin.dashboard"))
