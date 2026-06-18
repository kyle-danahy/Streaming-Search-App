import importlib.util
import json
import os
import subprocess
import sys
import time
import types
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.database.database_helper import LOCAL_DATABASE_URL
from src.tests.test_data import TestData

os.environ.setdefault('WATCHMODE_API_KEY', 'test-api-key')

COMPOSE_FILE = Path(__file__).resolve().parents[1] / 'database' / 'docker-compose.yaml'


def make_mock_url_response(payload):
    """Build a mock urllib response for a JSON Watchmode API payload."""
    mock_response = Mock()
    mock_response.read.return_value = json.dumps(payload).encode('utf-8')
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)
    return mock_response


@pytest.fixture
def mock_watchmode_api():
    """Mock Watchmode search and streaming-service API calls."""
    search_payload = TestData.get_sample_search_results()

    with patch(
        'src.data_collector.data_collector.urllib.request.urlopen',
        return_value=make_mock_url_response(search_payload),
    ) as mock_urlopen, patch(
        'src.data_collector.data_collector.get_available_streaming_services',
        side_effect=[['Netflix', 'Hulu'], ['Peacock', 'Amazon Prime']],
    ) as mock_get_services, patch(
        'src.data_collector.data_collector.send_api_results',
    ) as mock_send_api_results, patch(
        'src.messaging.rabbit_consumer.consume_api_results',
        return_value=search_payload,
    ) as mock_consume_api_results:
        yield {
            'urlopen': mock_urlopen,
            'get_available_streaming_services': mock_get_services,
            'send_api_results': mock_send_api_results,
            'consume_api_results': mock_consume_api_results,
            'search_payload': search_payload,
        }


def _start_postgres():
    """Start the local Postgres container and wait until it accepts connections."""
    subprocess.run(
        ['docker', 'compose', '-f', str(COMPOSE_FILE), 'up', '-d'],
        check=True,
    )

    time.sleep(3)
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

    raise RuntimeError(
        'Postgres did not become ready in time, try running again or increase the sleep time.'
    )


def pytest_configure(config):
    """Ensure tests use the local Docker Postgres database."""
    os.environ['DATABASE_URL'] = LOCAL_DATABASE_URL
    os.environ['SQLALCHEMY_DATABASE_URI'] = LOCAL_DATABASE_URL
    if not os.environ.get('CI'):
        _start_postgres()
