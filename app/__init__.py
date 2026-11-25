import os
import logging
from flask import Flask, render_template
from app.config import Config, config_by_name
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_class=None):
    if config_class is None:
        env_name = os.getenv("FLASK_ENV", "development").lower()
        config_class = config_by_name.get(env_name, Config)

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.catalog.routes import bp as catalog_bp
    from app.cart.routes import bp as cart_bp
    from app.auth.routes import bp as auth_bp
    from app.orders.routes import bp as orders_bp
    from app.payments.routes import bp as payments_bp
    from app.admin.routes import bp as admin_bp

    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)

    # Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Custom Error Pages
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Context processors
    @app.context_processor
    def inject_global_data():
        from app.cart.services import cart_items_count
        from app.models import Category
        try:
            categories = Category.query.all()
            cart_count = cart_items_count()
        except Exception:
            categories = []
            cart_count = 0
        return {
            "global_categories": categories,
            "cart_count": cart_count,
            "site_name": "bookish",
            "paystack_public_key": app.config.get("PAYSTACK_PUBLIC_KEY"),
        }

    # Template filters
    @app.template_filter("kes")
    def format_kes(value):
        try:
            return f"KES {int(value):,}"
        except (ValueError, TypeError):
            return f"KES {value}"

    # CLI commands
    @app.cli.command("seed-db")
    def seed_db():
        from app.seeds import seed_data
        seed_data()
        print("Database seeded successfully!")

    return app
