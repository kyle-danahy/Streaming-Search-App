"""Unit tests for the data collector module."""

import os
import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from src.data_collector.data_collector import (
    get_available_streaming_services,
    write_results_to_db,
    db,
    StreamingSearch,
    init_app,
)
from src.database.database_helper import get_database_uri


@pytest.fixture
def collector_app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'postgresql://flaskuser:flaskpass@localhost:5432/flaskdb'
    )
    init_app(app)
    return app


@pytest.fixture
def db_session(collector_app):
    """Create a test database session."""
    with collector_app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def pytest_configure(config):
    """Ensure tests use the Docker Postgres database URL."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = get_database_uri()
        os.environ['DATABASE_URL'] = database_url

    if 'SQLALCHEMY_DATABASE_URI' not in os.environ:
        os.environ['SQLALCHEMY_DATABASE_URI'] = database_url


# TODO: replace REST calls with mocks
class TestWriteResultsToDb:
    """Test suite for the write_results_to_db() function."""

    def test_write_results_to_db_single_record(self, db_session, collector_app):
        """Test write_results_to_db writes a single record to the database."""
        test_data = {'results': [{'id': 1, 'name': 'Breaking Bad'}]}

        with collector_app.app_context():
            write_results_to_db(test_data)

            # Query the database to verify the record was created
            records = StreamingSearch.query.all()
            assert len(records) == 1
            assert json.loads(records[0].search_query) == test_data

    def test_write_results_to_db_multiple_records(self, db_session, collector_app):
        """Test write_results_to_db can write multiple records."""
        test_data_1 = {'results': [{'id': 1, 'name': 'Breaking Bad'}]}
        test_data_2 = {'results': [{'id': 2, 'name': 'The Office'}]}

        with collector_app.app_context():
            write_results_to_db(test_data_1)
            write_results_to_db(test_data_2)

            records = StreamingSearch.query.all()
            assert len(records) == 2
            assert json.loads(records[0].search_query) == test_data_1
            assert json.loads(records[1].search_query) == test_data_2

    def test_write_results_to_db_stores_json(self, db_session, collector_app):
        """Test that write_results_to_db stores data as JSON."""
        test_data = {'search': 'test_query', 'results': []}

        with collector_app.app_context():
            write_results_to_db(test_data)

            record = StreamingSearch.query.first()
            assert isinstance(record.search_query, str)
            assert json.loads(record.search_query) == test_data


class TestGetAvailableStreamingServices:
    """Test suite for get_available_streaming_services()."""

    def test_get_available_streaming_services_parses_service_names(self):
        """Test that service names are extracted from the Watchmode API response."""
        api_response = [
            {'name': 'Netflix'},
            {'name': 'Hulu'},
        ]
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(api_response).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)

        with patch('src.data_collector.data_collector.urllib.request.urlopen',
                   return_value=mock_response) as mock_urlopen:
            services = get_available_streaming_services(123)

        assert services == ['Netflix', 'Hulu']
        mock_urlopen.assert_called_once_with(
            'https://api.watchmode.com/v1/title/123/sources/?apiKey=Ueg5Sw7ZedERgV0pzRjKdPa30qCteVX9Iua6QtQc'
        )
