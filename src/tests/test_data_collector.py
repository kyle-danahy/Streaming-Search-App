"""Unit tests for the data collector module."""

import json
import pytest
from flask import Flask
from src.data_collector.data_collector import (
    write_results_to_db,
    db,
    StreamingSearch,
    init_app,
)


@pytest.fixture
def collector_app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    init_app(app)
    return app


@pytest.fixture
def db_session(collector_app):
    """Create a test database session."""
    with collector_app.app_context():
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
