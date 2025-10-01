"""Wait for dependent services (Postgres, Redis) and initialize DB.

Usage:
  source venv/bin/activate
  export DATABASE_URL=postgresql://hermes:hermes_password@localhost:5432/hermes
  export REDIS_URL=redis://localhost:6379/0
  python backend/scripts/wait_for_services.py --timeout 60
"""
import os
import time
import argparse
import logging

logger = logging.getLogger('wait_for_services')
logging.basicConfig(level=logging.INFO)


def wait_for_postgres(dsn, timeout=60):
    try:
        import psycopg2
        from psycopg2 import OperationalError
    except Exception:
        logger.warning('psycopg2 not installed; skipping Postgres wait')
        return True

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            conn = psycopg2.connect(dsn)
            conn.close()
            logger.info('Postgres is available')
            return True
        except OperationalError as e:
            logger.info('Waiting for Postgres... (%s)', e)
            time.sleep(2)
    logger.error('Timed out waiting for Postgres')
    return False


def wait_for_redis(url, timeout=30):
    try:
        import redis
    except Exception:
        logger.warning('redis-py not installed; skipping Redis wait')
        return True

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = redis.from_url(url)
            r.ping()
            logger.info('Redis is available')
            return True
        except Exception as e:
            logger.info('Waiting for Redis... (%s)', e)
            time.sleep(1)
    logger.error('Timed out waiting for Redis')
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()

    db_url = os.getenv('DATABASE_URL')
    redis_url = os.getenv('REDIS_URL')

    ok = True
    if db_url and db_url.startswith('postgres'):
        ok = wait_for_postgres(db_url, timeout=args.timeout) and ok

    if redis_url:
        ok = wait_for_redis(redis_url, timeout=args.timeout) and ok

    if ok:
        # try to import db and init
        try:
            # attempt package import
            from backend import db
            db.init_db()
            logger.info('db.init_db() invoked')
        except Exception as e:
            logger.warning('Could not run db.init_db(): %s', e)
    else:
        logger.error('Dependent services not ready')


if __name__ == '__main__':
    main()
