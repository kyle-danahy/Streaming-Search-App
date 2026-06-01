"""Unit tests for the Flask app."""

import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.app_context():
        from src.data_collector import data_collector

        data_collector.db.create_all()
    with app.test_client() as test_client:
        yield test_client


class TestQueryStreamingApi:
    """Test suite for the query_streaming_api() function."""

    def test_query_streaming_api_with_normal_text(self, client):
        """Test query_streaming_api with normal text input."""
        response = client.post('/query_streaming_api', data={'movie_show_title': 'Breaking Bad'})
        assert response.status_code == 200
        assert 'You entered: Breaking Bad' in response.data.decode()

    # @pytest.mark.skip
    def test_query_streaming_api_with_no_form_data(self, client):
        """Test query_streaming_api when form data is missing."""
        response = client.post('/query_streaming_api', data={})
        assert response.status_code == 200
        assert response.data.decode() is not None

    # @pytest.mark.skip
    def test_main_route_get(self, client):
        """Test the main route returns a form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<form' in response.data
        assert b'movie_show_title' in response.data
