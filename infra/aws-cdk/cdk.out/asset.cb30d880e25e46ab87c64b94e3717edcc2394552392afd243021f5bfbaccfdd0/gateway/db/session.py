"""
Database session management for Relay Gateway.

Provides SQLAlchemy session management for PostgreSQL audit ledger.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Base class for ORM models
Base = declarative_base()


class DatabaseConfig:
    """Database configuration."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "relay",
        username: str = "relay",
        password: str = "relay_password",
        pool_size: int = 10,
        max_overflow: int = 20,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    @property
    def connection_string(self) -> str:
        """Build PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None

    def initialize(self):
        """Initialize database engine and session factory."""
        self.engine = create_engine(
            self.config.connection_string,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            echo=False,  # Set to True for SQL query logging
        )

        # Enable autocommit mode for read queries
        @event.listens_for(self.engine, "connect")
        def set_readonly_for_select(dbapi_conn, connection_record):
            """Optimize read-only queries."""
            pass  # Can add connection-level optimizations here

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables (use migrations in production)."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            with db_manager.get_session() as session:
                session.add(record)
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()


# Global database manager instance (initialized in main.py)
db_manager: DatabaseManager = None


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()
