"""Unit tests for the Flask app."""

import pytest

from src.database import database_helper


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    from src.app import app

    app.config['TESTING'] = True
    with app.app_context():
        database_helper.db.create_all()
    with app.test_client() as test_client:
        yield test_client


class TestQueryStreamingApi:
    """Test suite for the query_streaming_api() function."""

    def test_query_streaming_api_with_normal_text(self, client, mock_watchmode_api):
        """Test query_streaming_api with normal text input."""
        response = client.post('/query_streaming_api', data={'movie_show_title': 'Breaking Bad'})
        assert response.status_code == 200
        assert 'You entered: Breaking Bad' in response.data.decode()
        mock_watchmode_api['urlopen'].assert_called_once()

    def test_query_streaming_api_with_no_form_data(self, client, mock_watchmode_api):
        """Test query_streaming_api when form data is missing."""
        response = client.post('/query_streaming_api', data={})
        assert response.status_code == 200
        assert response.data.decode() is not None
        mock_watchmode_api['urlopen'].assert_called_once()

    def test_main_route_get(self, client):
        """Test the main route returns a form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<form' in response.data
        assert b'movie_show_title' in response.data
