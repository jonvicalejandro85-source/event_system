import os
from dotenv import load_dotenv

# ✅ Load environment variables early
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///events.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Mail configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() in ("1", "true", "yes")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Debugging: show loaded config in console
    print(f"📧 MAIL_SERVER={MAIL_SERVER}")
    print(f"📧 MAIL_USERNAME={MAIL_USERNAME}")