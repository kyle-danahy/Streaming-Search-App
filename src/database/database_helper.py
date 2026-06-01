#!/usr/bin/env python3
import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
except ImportError:
    pass


def get_database_uri():
    """Return the database URI for SQLAlchemy.

    Priority order:
    1. app config provides SQLALCHEMY_DATABASE_URI
    2. environment variable SQLALCHEMY_DATABASE_URI / DATABASE_URL
    3. Docker Postgres defaults from environment variables
    """
    configured_uri = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    if configured_uri:
        return configured_uri.replace('postgres://', 'postgresql://', 1)

    postgres_user = os.environ.get('POSTGRES_USER', 'flaskuser')
    postgres_password = os.environ.get('POSTGRES_PASSWORD', 'flaskpass')
    postgres_db = os.environ.get('POSTGRES_DB', 'flaskdb')
    postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
    postgres_port = os.environ.get('POSTGRES_PORT', '5432')

    return (
        f'postgresql://{postgres_user}:{postgres_password}'
        f'@{postgres_host}:{postgres_port}/{postgres_db}'
    )


def clear_database(db, individual_result, streaming_search):
    """Clear the search and individual result tables before a new API query."""
    db.session.query(individual_result).delete()
    db.session.query(streaming_search).delete()
    db.session.commit()
