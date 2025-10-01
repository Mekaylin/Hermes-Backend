import os
import logging

logger = logging.getLogger(__name__)

# Try to import SQLAlchemy; if it fails (e.g. incompatible Python version
# or not installed) make the module resilient so the app can still run in
# a degraded mode without DB persistence.
HAS_SQLALCHEMY = False
try:
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import sessionmaker, declarative_base
    from sqlalchemy.exc import OperationalError

    HAS_SQLALCHEMY = True
except Exception as e:  # pragma: no cover - defensive
    logger.warning("SQLAlchemy not available or failed to import: %s", e)


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/hermes_dev')

if HAS_SQLALCHEMY:
    # Create engine lazily to avoid raising during import time in environments
    # where Postgres is not available.
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base = declarative_base()
    metadata = MetaData()
else:
    engine = None
    SessionLocal = None
    Base = None
    metadata = None


def init_db():
    """Initialize DB tables. Safe no-op when SQLAlchemy is unavailable.

    Import models lazily only when SQLAlchemy exists so imports do not fail
    during app startup in minimal environments.
    """
    if not HAS_SQLALCHEMY:
        logger.warning("Skipping DB initialization because SQLAlchemy is unavailable.")
        return
    # Import models here to ensure they are registered on the Base
    from . import models  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        # Do not crash the app when DB is unreachable during local dev.
        logger.warning("Could not initialize DB (is Postgres running?): %s", e)
