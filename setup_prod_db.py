"""
One-time setup script for the production database.
Run locally with your production DATABASE_URL to create tables and seed data.

Usage:
    set DATABASE_URL=postgresql://...
    set FLASK_ENV=production
    set SECRET_KEY=your-secret-key
    set PAYSTACK_SECRET_KEY=sk_live_or_test_xxx
    python setup_prod_db.py
"""
import os
import sys

# Temporarily relax production validation for initial setup
os.environ.setdefault("FLASK_ENV", "production")

from app import create_app
from app.extensions import db
from app.models import User, Category, Book, BookVariant, Cart, CartItem, Order, OrderItem, Payment, WebhookEvent, NewsletterSubscriber

app = create_app()

with app.app_context():
    print("Creating all tables...")
    db.create_all()
    print("Tables created successfully!")

    # Check if data already exists
    if Category.query.first():
        print("Data already exists — skipping seed.")
    else:
        print("Seeding data...")
        from app.seeds import seed_data
        seed_data()
        print("Database seeded successfully!")

    print("\nDone! Your production database is ready.")
