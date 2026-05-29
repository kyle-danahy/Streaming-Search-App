"""Unit tests for the Flask app."""

import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


class TestEchoInput:
    """Test suite for the echo_input() function."""

    def test_echo_input_with_normal_text(self, client):
        """Test echo_input with normal text input."""
        response = client.post('/echo_user_input', data={'user_input': 'Hello World'})
        assert response.status_code == 200
        assert response.data.decode() == 'You entered: Hello World'

    def test_echo_input_with_no_form_data(self, client):
        """Test echo_input when form data is missing."""
        response = client.post('/echo_user_input', data={})
        assert response.status_code == 200
        assert response.data.decode() == 'You entered: '

    def test_main_route_get(self, client):
        """Test the main route returns a form."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<form' in response.data
        assert b'user_input' in response.data
