"""Unit tests for the RabbitMQ producer and consumer modules."""

import json
from unittest.mock import Mock, patch

import pytest

import src.messaging.rabbit_consumer as rabbit_consumer
import src.messaging.rabbit_producer as rabbit_producer
from src.tests.test_data import TestData


@pytest.fixture(autouse=True)
def reset_rabbitmq_connections():
    """Reset module-level connection state between tests."""
    rabbit_producer._connection = None
    rabbit_producer._channel = None
    rabbit_consumer._connection = None
    rabbit_consumer._channel = None
    yield
    rabbit_producer._connection = None
    rabbit_producer._channel = None
    rabbit_consumer._connection = None
    rabbit_consumer._channel = None


@pytest.fixture
def mock_channel():
    """Provide a mock RabbitMQ channel."""
    channel = Mock()
    channel.is_closed = False
    return channel


@pytest.fixture
def mock_connection(mock_channel):
    """Provide a mock RabbitMQ connection that returns mock_channel."""
    connection = Mock()
    connection.channel.return_value = mock_channel
    return connection


class TestRabbitProducer:
    """Test suite for rabbit_producer.py."""

    @patch('src.messaging.rabbit_producer.pika.BlockingConnection')
    def test_send_api_results_publishes_json_to_queue(
        self, mock_blocking_connection, mock_connection, mock_channel
    ):
        """Test send_api_results declares the queue and publishes JSON."""
        mock_blocking_connection.return_value = mock_connection
        results = TestData.get_sample_search_results()

        rabbit_producer.send_api_results(results)

        mock_channel.queue_declare.assert_called_once_with(
            queue='api_results', durable=True
        )
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='api_results',
            body=json.dumps(results),
        )

    @patch('src.messaging.rabbit_producer.pika.BlockingConnection')
    def test_get_channel_reuses_open_channel(
        self, mock_blocking_connection, mock_connection, mock_channel
    ):
        """Test _get_channel reuses an existing open channel."""
        mock_blocking_connection.return_value = mock_connection

        first_channel = rabbit_producer._get_channel()
        second_channel = rabbit_producer._get_channel()

        assert first_channel is second_channel
        mock_blocking_connection.assert_called_once()

    @patch('src.messaging.rabbit_producer.pika.BlockingConnection')
    def test_get_channel_reconnects_when_channel_closed(
        self, mock_blocking_connection, mock_connection
    ):
        """Test _get_channel opens a new connection when the channel is closed."""
        first_channel = Mock(is_closed=False)
        second_channel = Mock(is_closed=False)
        mock_connection.channel.side_effect = [first_channel, second_channel]
        mock_blocking_connection.return_value = mock_connection

        open_channel = rabbit_producer._get_channel()
        first_channel.is_closed = True
        reconnected_channel = rabbit_producer._get_channel()

        assert open_channel is first_channel
        assert reconnected_channel is second_channel
        assert mock_blocking_connection.call_count == 2

    @patch('src.messaging.rabbit_producer.pika.ConnectionParameters')
    @patch('src.messaging.rabbit_producer.pika.BlockingConnection')
    def test_get_channel_uses_rabbitmq_host_env(
        self,
        mock_blocking_connection,
        mock_connection_parameters,
        mock_connection,
        mock_channel,
        monkeypatch,
    ):
        """Test _get_channel uses the RABBITMQ_HOST environment variable."""
        monkeypatch.setenv('RABBITMQ_HOST', 'rabbit.example.com')
        mock_blocking_connection.return_value = mock_connection

        rabbit_producer._get_channel()

        mock_connection_parameters.assert_called_once_with(host='rabbit.example.com')


class TestRabbitConsumer:
    """Test suite for rabbit_consumer.py."""

    @patch('src.messaging.rabbit_consumer.pika.BlockingConnection')
    def test_consume_api_results_returns_parsed_message(
        self, mock_blocking_connection, mock_connection, mock_channel
    ):
        """Test consume_api_results returns parsed JSON when a message exists."""
        mock_blocking_connection.return_value = mock_connection
        payload = TestData.get_sample_search_results()
        method_frame = Mock()
        mock_channel.basic_get.return_value = (
            method_frame,
            None,
            json.dumps(payload).encode('utf-8'),
        )

        result = rabbit_consumer.consume_api_results()

        assert result == payload
        mock_channel.queue_declare.assert_called_once_with(
            queue='api_results', durable=True
        )
        mock_channel.basic_get.assert_called_once_with(
            queue='api_results', auto_ack=True
        )

    @patch('src.messaging.rabbit_consumer.pika.BlockingConnection')
    def test_consume_api_results_returns_none_when_queue_empty(
        self, mock_blocking_connection, mock_connection, mock_channel
    ):
        """Test consume_api_results returns None when the queue is empty."""
        mock_blocking_connection.return_value = mock_connection
        mock_channel.basic_get.return_value = (None, None, None)

        assert rabbit_consumer.consume_api_results() is None

    @patch('src.messaging.rabbit_consumer.pika.BlockingConnection')
    def test_get_channel_reuses_open_channel(
        self, mock_blocking_connection, mock_connection, mock_channel
    ):
        """Test _get_channel reuses an existing open channel."""
        mock_blocking_connection.return_value = mock_connection

        first_channel = rabbit_consumer._get_channel()
        second_channel = rabbit_consumer._get_channel()

        assert first_channel is second_channel
        mock_blocking_connection.assert_called_once()

    @patch('src.messaging.rabbit_consumer.pika.BlockingConnection')
    def test_get_channel_reconnects_when_channel_closed(
        self, mock_blocking_connection, mock_connection
    ):
        """Test _get_channel opens a new connection when the channel is closed."""
        first_channel = Mock(is_closed=False)
        second_channel = Mock(is_closed=False)
        mock_connection.channel.side_effect = [first_channel, second_channel]
        mock_blocking_connection.return_value = mock_connection

        open_channel = rabbit_consumer._get_channel()
        first_channel.is_closed = True
        reconnected_channel = rabbit_consumer._get_channel()

        assert open_channel is first_channel
        assert reconnected_channel is second_channel
        assert mock_blocking_connection.call_count == 2
