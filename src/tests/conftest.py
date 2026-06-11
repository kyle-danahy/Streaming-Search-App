import os
import subprocess
import time
from pathlib import Path

from src.database.database_helper import LOCAL_DATABASE_URL

COMPOSE_FILE = Path(__file__).resolve().parents[1] / 'database' / 'docker-compose.yaml'


def _start_postgres():
    """Start the local Postgres container and wait until it accepts connections."""
    subprocess.run(
        ['docker', 'compose', '-f', str(COMPOSE_FILE), 'up', '-d'],
        check=True,
    )

    """Sleep for 5 seconds to give the db time to boot."""
    time.sleep(5)
    result = subprocess.run(
        [
            'docker', 'compose', '-f', str(COMPOSE_FILE),
            'exec', '-T', 'postgres',
            'pg_isready', '-U', 'flaskuser', '-d', 'flaskdb',
        ],
        capture_output=True,
    )
    if result.returncode == 0:
        return

    raise RuntimeError('Postgres did not become ready in time, try running again or increase the sleep time.')


def pytest_configure(config):
    """Ensure tests use the local Docker Postgres database."""
    os.environ['DATABASE_URL'] = LOCAL_DATABASE_URL
    os.environ['SQLALCHEMY_DATABASE_URI'] = LOCAL_DATABASE_URL
    if not os.environ.get('CI'):
        _start_postgres()
