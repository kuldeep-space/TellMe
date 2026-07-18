"""
SQLite Connection Manager.

Provides thread-safe session factories for SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import get_settings


class Database:
    """Manages the SQLAlchemy engine and session factory."""

    def __init__(self, db_url: str | None = None) -> None:
        """Initialize the database engine."""
        url = db_url or f"sqlite:///{get_settings().database_url}"
        self.engine = create_engine(url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self):
        """Yield a database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
