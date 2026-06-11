"""Unit tests for the data collector module."""

import json
from unittest.mock import patch

import pytest
from flask import Flask
from src.data_collector.data_collector import (
    get_available_streaming_services,
    search,
    write_results_to_db,
    db,
    StreamingSearch,
    IndividualResult,
    init_app,
    API_KEY,
)
from src.database.database_helper import LOCAL_DATABASE_URL
from src.tests.conftest import make_mock_url_response
from src.tests.test_data import TestData


@pytest.fixture
def collector_app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = LOCAL_DATABASE_URL
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


class TestWriteResultsToDb:
    """Test suite for the write_results_to_db() function."""

    def test_write_results_to_db_single_record(self, db_session, collector_app):
        """Test write_results_to_db writes a single record to the database."""
        test_data = {'results': [{'id': 1, 'name': 'Breaking Bad'}]}

        with collector_app.app_context():
            write_results_to_db(test_data)

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

    def test_write_results_to_db_stores_individual_results(self, db_session, collector_app):
        """Test write_results_to_db stores individual results using mocked sources API."""
        test_data = TestData.get_sample_search_results()

        with patch(
            'src.data_collector.data_collector.get_available_streaming_services',
            return_value=['Netflix'],
        ) as mock_get_services, collector_app.app_context():
            write_results_to_db(test_data)

            records = IndividualResult.query.all()
            assert len(records) == 2
            assert records[0].result_name == 'Breaking Bad'
            assert json.loads(records[0].available_streaming_services) == ['Netflix']
            assert mock_get_services.call_count == 2


class TestSearch:
    """Test suite for search()."""

    def test_search_calls_watchmode_api_and_writes_results(
        self, db_session, collector_app, mock_watchmode_api
    ):
        """Test search uses the Watchmode API and persists the response."""
        search_payload = mock_watchmode_api['search_payload']

        with collector_app.app_context():
            results = search({'search_field': 'name', 'search_value': 'Breaking Bad'})

        assert results == search_payload
        mock_watchmode_api['urlopen'].assert_called_once()
        called_url = mock_watchmode_api['urlopen'].call_args[0][0]
        assert called_url.startswith('https://api.watchmode.com/v1/search/?')
        assert f'apiKey={API_KEY}' in called_url
        assert 'search_value=Breaking+Bad' in called_url


class TestGetAvailableStreamingServices:
    """Test suite for get_available_streaming_services()."""

    def test_get_available_streaming_services_parses_service_names(self):
        """Test that service names are extracted from the Watchmode API response."""
        api_response = [
            {'name': 'Netflix'},
            {'name': 'Hulu'},
        ]

        with patch(
            'src.data_collector.data_collector.urllib.request.urlopen',
            return_value=make_mock_url_response(api_response),
        ) as mock_urlopen:
            services = get_available_streaming_services(123)

        assert services == ['Netflix', 'Hulu']
        mock_urlopen.assert_called_once_with(
            f'https://api.watchmode.com/v1/title/123/sources/?apiKey={API_KEY}'
        )
