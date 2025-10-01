"""Create database tables for the Hermes backend.

Run with the project's venv:

  source venv/bin/activate
  python scripts/init_db.py

This script is safe to run if SQLAlchemy is missing or the DB is unreachable.
"""
import logging
from pathlib import Path
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('init_db')

# Try several import strategies so the script works run from repo root or backend/
db = None
try:
    # when executed as module: python -m backend.scripts.init_db
    from backend import db as db
except Exception:
    try:
        # when run from backend/ directly
        import db as db
    except Exception:
        # fallback: add parent dir to sys.path and try again
        p = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(p))
        try:
            from backend import db as db
        except Exception as e:
            logger.error('Could not import db module after trying multiple paths: %s', e)
            sys.exit(1)

def main():
    logger.info('Initializing DB (if SQLAlchemy and DB are available)...')
    # If SQLAlchemy is present, use the project's init_db which may create
    # tables on the configured DATABASE_URL. If SQLAlchemy isn't available
    # (or DB unreachable) we'll explicitly apply a local SQLite fallback.
    if getattr(db, 'HAS_SQLALCHEMY', False):
        try:
            db.init_db()
            logger.info('init_db via SQLAlchemy completed')
        except Exception as e:
            logger.warning('SQLAlchemy-based init_db failed: %s', e)
    else:
        logger.warning('SQLAlchemy not present; applying SQLite fallback')
        try:
            import sqlite3
            sql_path = Path(__file__).resolve().parents[1] / 'init_db.sql'
            if sql_path.exists():
                logger.info('Applying SQL from %s into local sqlite file', sql_path)
                db_file = Path.cwd() / 'hermes_dev.sqlite3'
                conn = sqlite3.connect(str(db_file))
                with open(sql_path, 'r') as fh:
                    sql = fh.read()
                conn.executescript(sql)
                conn.commit()
                conn.close()
                logger.info('SQLite fallback DB created at %s', db_file)
            else:
                logger.error('No SQL fallback file found at %s', sql_path)
        except Exception as e2:
            logger.error('SQLite fallback also failed: %s', e2)
    logger.info('init_db completed')

if __name__ == '__main__':
    main()
