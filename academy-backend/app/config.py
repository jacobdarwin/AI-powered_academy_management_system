import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _database_uri() -> str:
    value = os.getenv("DATABASE_URL", "sqlite:///academy.db")
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-change-me-32")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development-jwt-secret-change-me-32")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))
    _frontend_dir = Path(os.getenv("FRONTEND_DIR", "../login-page"))
    FRONTEND_DIR = (
        _frontend_dir if _frontend_dir.is_absolute() else (BASE_DIR / _frontend_dir).resolve()
    )
    JSON_SORT_KEYS = False
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))).resolve()
    MATERIAL_MAX_BYTES = int(os.getenv("MATERIAL_MAX_BYTES", "16777216"))


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    JWT_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


def get_config() -> type[Config]:
    environment = os.getenv("FLASK_ENV", "development").lower()
    return {
        "testing": TestingConfig,
        "production": ProductionConfig,
    }.get(environment, DevelopmentConfig)
