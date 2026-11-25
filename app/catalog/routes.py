from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.extensions import db
from app.models import Book, Category, NewsletterSubscriber

bp = Blueprint("catalog", __name__)

@bp.get("/")
def home():
    # Fresh off the shelf: 4 featured books
    fresh_books = Book.query.filter_by(is_active=True).order_by(Book.created_at.desc()).limit(4).all()
    categories = Category.query.all()
    bestsellers = Book.query.filter_by(is_active=True, tag="Bestseller").limit(4).all()
    if not bestsellers:
        bestsellers = fresh_books

    return render_template(
        "home.html",
        fresh_books=fresh_books,
        categories=categories,
        bestsellers=bestsellers,
    )

@bp.get("/shop")
def shop():
    genre_slug = request.args.get("genre", "all").strip().lower()
    sort_by = request.args.get("sort", "newest").strip()
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 12

    books_query = Book.query.filter_by(is_active=True)

    if genre_slug and genre_slug != "all":
        category = Category.query.filter_by(slug=genre_slug).first()
        if category:
            books_query = books_query.filter(Book.category_id == category.id)

    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.description.ilike(f"%{query}%"))
        )

    if sort_by == "price_low":
        books_query = books_query.order_by(Book.price_kes.asc())
    elif sort_by == "price_high":
        books_query = books_query.order_by(Book.price_kes.desc())
    else:
        books_query = books_query.order_by(Book.created_at.desc())

    pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()

    return render_template(
        "shop.html",
        pagination=pagination,
        books=pagination.items,
        categories=categories,
        current_genre=genre_slug,
        current_sort=sort_by,
        search_query=query,
    )

@bp.get("/book/<slug>")
def product(slug):
    book = Book.query.filter_by(slug=slug, is_active=True).first_or_404()
    # Recommendations: more like this (same category or others, excluding current book)
    similar_books = (
        Book.query.filter(Book.id != book.id, Book.category_id == book.category_id, Book.is_active == True)
        .limit(4)
        .all()
    )
    if len(similar_books) < 4:
        extra = (
            Book.query.filter(Book.id != book.id, Book.id.notin_([b.id for b in similar_books]), Book.is_active == True)
            .limit(4 - len(similar_books))
            .all()
        )
        similar_books.extend(extra)

    return render_template("product.html", book=book, similar_books=similar_books)

@bp.post("/newsletter")
def newsletter():
    email = request.form.get("email", "").strip().lower()
    if not email or "@" not in email:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "error", "message": "Please enter a valid email address."}), 400
        flash("Please enter a valid email address.", "error")
        return redirect(request.referrer or url_for("catalog.home"))

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if not existing:
        sub = NewsletterSubscriber(email=email)
        db.session.add(sub)
        db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "success", "message": "You're on the list! Welcome to the bookish club."})

    flash("You're on the list! Welcome to the bookish club.", "success")
    return redirect(request.referrer or url_for("catalog.home"))
