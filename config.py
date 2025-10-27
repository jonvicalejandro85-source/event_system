import os
from dotenv import load_dotenv
# ✅ Load environment variables early
load_dotenv()

class Config:
    # SECRET KEY (keep this for session security)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')

    # DATABASE CONFIG
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///events.db')

    # ✅ Fix for SQLAlchemy URI scheme (Render gives 'postgres://' but SQLAlchemy needs 'postgresql://')
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Mail configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # Debugging: show loaded config in console
    print(f"📧 MAIL_SERVER={MAIL_SERVER}")
    print(f"📧 MAIL_USERNAME={MAIL_USERNAME}")