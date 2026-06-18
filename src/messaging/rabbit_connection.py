#!/usr/bin/env python3
import os

import pika


def get_connection_parameters():
    """Build pika connection parameters from environment variables."""
    url = os.environ.get('CLOUDAMQP_URL')
    api_key = os.environ.get('CLOUDAMQP_APIKEY')
    if url:
        parameters = pika.URLParameters(url)
        if api_key:
            parameters.credentials = pika.PlainCredentials(
                parameters.credentials.username,
                api_key,
            )
        return parameters
    host = os.environ.get('RABBITMQ_HOST', 'localhost')
    return pika.ConnectionParameters(host=host)
