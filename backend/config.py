"""
Configuration for the Flask application.

Supports local (SQLite) and production (RDS PostgreSQL) modes.
"""

import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-x25176862")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")
    USE_LOCAL_MOCKS = os.environ.get("USE_LOCAL_MOCKS", "true").lower() == "true"
    S3_BUCKET = os.environ.get("S3_BUCKET", "transit-planner-assets")
    SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "http://localhost:4566/queue/trip-planning")
    CLOUDFRONT_DOMAIN = os.environ.get("CLOUDFRONT_DOMAIN", "d1234567890.cloudfront.net")


class DevelopmentConfig(Config):
    """Development configuration using SQLite."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///transit_planner.db"
    )


class ProductionConfig(Config):
    """Production configuration using RDS PostgreSQL."""
    DEBUG = False
    USE_LOCAL_MOCKS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://user:pass@rds-endpoint:5432/transit_planner"
    )


class TestingConfig(Config):
    """Testing configuration using in-memory SQLite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    USE_LOCAL_MOCKS = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
