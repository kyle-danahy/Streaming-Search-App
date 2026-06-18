"""Data collector module for the streaming search application. It sends a request
to the Watchmode API and writes the results to a database."""
import json
import os
import sys
import urllib.request
from logging import basicConfig, getLogger, log
from urllib.parse import urlencode

from src.messaging.rabbit_producer import send_api_results

log = getLogger(__name__)

API_KEY = os.environ.get('WATCHMODE_API_KEY')


def search(query):
    """Helper function to perform a search using the Watchmode API. Calls the API
    and then writes the results to the database."""
    search_field = query['search_field']
    search_value = query['search_value']

    params = {
        'apiKey': API_KEY,
        'search_field': search_field,
        'search_value': search_value
    }

    url = f'https://api.watchmode.com/v1/search/?{urlencode(params)}'

    log.info("Querying Watchmode API with URL: %s", url)
    with urllib.request.urlopen(url) as response:
        results = json.loads(response.read().decode())
        title_count = len(results.get('title_results', []))
        log.info('Search completed with %s title results', title_count)
        send_api_results(results)

def get_available_streaming_services(title_id):
    """Helper function to query the Watchmode API for a list of available streaming
    services for a selected title."""
    url = f'https://api.watchmode.com/v1/title/{title_id}/sources/?apiKey={API_KEY}'
    list_of_streaming_services = []

    log.info("Querying Watchmode API for streaming services with URL: %s", url)
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        for item in data:
            list_of_streaming_services.append(item.get('name'))

    return list_of_streaming_services if list_of_streaming_services else ["Not Available"]


def main():
    """Collect streaming search data and write results to the database."""
    basicConfig(
        level=os.environ.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    if not API_KEY:
        log.error('WATCHMODE_API_KEY environment variable is required')
        sys.exit(1)

    search_field = os.environ.get('SEARCH_FIELD', 'name')
    search_value = os.environ.get('SEARCH_VALUE')
    if not search_value:
        log.error('SEARCH_VALUE environment variable is required')
        sys.exit(1)

    log.info('Running search for %s=%r', search_field, search_value)
    search({'search_field': search_field, 'search_value': search_value})


if __name__ == '__main__':
    main()
