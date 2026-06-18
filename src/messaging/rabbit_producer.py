#!/usr/bin/env python3
import json
import os

import pika

_connection = None
_channel = None


def _get_channel():
    """Establish a connection to RabbitMQ when publishing is needed."""
    global _connection, _channel
    if _channel is None or _channel.is_closed:
        host = os.environ.get('RABBITMQ_HOST', 'localhost')
        _connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
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
