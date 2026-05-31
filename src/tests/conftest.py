import os

from src.database.database_helper import get_database_uri


def pytest_configure(config):
    """Ensure tests use the Docker Postgres database URL."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = get_database_uri()
        os.environ['DATABASE_URL'] = database_url

    if 'SQLALCHEMY_DATABASE_URI' not in os.environ:
        os.environ['SQLALCHEMY_DATABASE_URI'] = database_url
