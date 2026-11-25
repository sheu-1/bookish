import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"

# Vercel has a read-only filesystem — only create instance dir locally
try:
    INSTANCE_DIR.mkdir(exist_ok=True)
except OSError:
    pass

load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-bookish-12345")
    db_path = (INSTANCE_DIR / "bookish.db").as_posix()
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{db_path}"
    if SQLALCHEMY_DATABASE_URI.startswith("sqlite:///instance/"):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    # Fix for Heroku/Render postgres prefix:
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)

    # Paystack Settings
    PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY") or os.getenv("EXPO_PUBLIC_PAYSTACK_PUBLIC_KEY") or "pk_test_bookish_placeholder"
    PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY") or os.getenv("EXPO_PUBLIC_PAYSTACK_SECRET_KEY") or "sk_test_bookish_placeholder"
    SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:5000")
    PAYSTACK_MOCK_ENABLED = os.getenv("PAYSTACK_MOCK_ENABLED", "false").lower() in ("true", "1", "yes")

    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    DEBUG = True
    PAYSTACK_MOCK_ENABLED = os.getenv("PAYSTACK_MOCK_ENABLED", "true").lower() in ("true", "1", "yes")

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PAYSTACK_MOCK_ENABLED = False

    @classmethod
    def validate_env(cls):
        secret = os.getenv("SECRET_KEY")
        if not secret or "dev-secret" in secret or len(secret) < 16:
            raise ValueError("PRODUCTION ERROR: SECRET_KEY must be set to a secure, random string in production.")
        paystack_key = os.getenv("PAYSTACK_SECRET_KEY")
        if not paystack_key or "placeholder" in paystack_key:
            raise ValueError("PRODUCTION ERROR: PAYSTACK_SECRET_KEY must be set to your live or test Paystack secret key.")

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    PAYSTACK_MOCK_ENABLED = True
    SESSION_COOKIE_SECURE = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestConfig,
    "default": DevelopmentConfig,
}
