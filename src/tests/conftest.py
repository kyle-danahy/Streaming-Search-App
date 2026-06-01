import os

from src.database.database_helper import LOCAL_DATABASE_URL


def pytest_configure(config):
    """Ensure tests use the local Docker Postgres database."""
    os.environ['DATABASE_URL'] = LOCAL_DATABASE_URL
    os.environ['SQLALCHEMY_DATABASE_URI'] = LOCAL_DATABASE_URL
