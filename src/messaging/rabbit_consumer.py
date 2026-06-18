#!/usr/bin/env python3
import json
import os
import sys

import pika

_connection = None
_channel = None


def _get_channel():
    """Establish a connection to RabbitMQ when consuming is needed."""
    global _connection, _channel
    if _channel is None or _channel.is_closed:
        host = os.environ.get('RABBITMQ_HOST', 'localhost')
        _connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        _channel = _connection.channel()
    return _channel


def consume_api_results():
    """Pull a single message from the api_results queue."""
    channel = _get_channel()
    channel.queue_declare(queue='api_results', durable=True)
    method_frame, _properties, body = channel.basic_get(queue='api_results', auto_ack=True)
    if method_frame:
        return json.loads(body)
    return None


def main():
    """Run a long-lived consumer for the api_results queue."""
    channel = _get_channel()
    channel.queue_declare(queue='api_results', durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='api_results', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)


if __name__ == '__main__':
    main()
