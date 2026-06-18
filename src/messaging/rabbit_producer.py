#!/usr/bin/env python3
import json

import pika

from src.messaging.rabbit_connection import get_connection_parameters

_connection = None
_channel = None


def _get_channel():
    """Establish a connection to RabbitMQ when publishing is needed."""
    global _connection, _channel
    if _channel is None or _channel.is_closed:
        _connection = pika.BlockingConnection(get_connection_parameters())
        _channel = _connection.channel()
    return _channel


def send_api_results(results):
    """Publish API search results to the api_results queue."""
    channel = _get_channel()
    channel.queue_declare(queue='api_results', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='api_results',
        body=json.dumps(results),
    )
