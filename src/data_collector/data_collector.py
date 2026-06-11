"""Data collector module for the streaming search application. It sends a request
to the Watchmode API and writes the results to a database."""
import json
import os
import sys
import urllib.request
from datetime import datetime
from logging import basicConfig, getLogger, log
from urllib.parse import urlencode

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from src.database.database_helper import get_database_uri

log = getLogger(__name__)

# Create the SQLAlchemy object without binding to a Flask app yet.
db = SQLAlchemy()
API_KEY = os.environ.get(
    'WATCHMODE_API_KEY',
    'Ueg5Sw7ZedERgV0pzRjKdPa30qCteVX9Iua6QtQc',
)


def init_app(app):
    """Initialize the SQLAlchemy object with the Flask application."""
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', get_database_uri())
    db.init_app(app)


class StreamingSearch(db.Model):
    """Define the database model that is used to store the search query."""
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    search_query = db.Column(db.Text, nullable=False)


class IndividualResult(db.Model):
    """Model to store individual results from a search."""
    id = db.Column(db.Integer, primary_key=True)
    search_datetime = db.Column(db.DateTime, db.ForeignKey('streaming_search.datetime'),
                                nullable=False)
    result_id = db.Column(db.Integer)
    result_name = db.Column(db.String(200))
    result_type = db.Column(db.String(50))
    available_streaming_services = db.Column(db.String(500))

    # optional relationship back to the search record
    search = db.relationship('StreamingSearch', backref=db.backref('results', lazy=True))

def write_results_to_db(data):
    """Helper function to write search results to the database."""
    search_query = json.dumps(data)
    new_search = StreamingSearch(search_query=search_query)
    new_search.datetime = datetime.now()
    log.info("Adding new search to database...")
    db.session.add(new_search)
    log.info("Parsing individual results...")
    write_individual_results(new_search)
    log.info("Writing to database...")
    db.session.commit()

def write_individual_results(search_record):
    """Separate the individual results to the results table."""
    search_data = json.loads(search_record.search_query)
    result_counter = 0
    for result in search_data.get('title_results', []):
        result_id = result.get('id')
        available_streaming_services = get_available_streaming_services(result_id)
        individual_result = IndividualResult(
            search_datetime=search_record.datetime,
            result_id=result.get('id'),
            result_name=result.get('name'),
            result_type=result.get('type'),
            available_streaming_services=json.dumps(available_streaming_services)
        )
        db.session.add(individual_result)
        result_counter += 1
    log.info("Added %s individual results to the database.", result_counter)

def get_most_recent_search():
    """Helper function to get the most recent search query from the database."""
    return StreamingSearch.query.order_by(StreamingSearch.datetime.desc()).first()

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
        data = json.loads(response.read().decode())
        write_results_to_db(data)
        return data

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


def create_app():
    """Create a minimal Flask app so SQLAlchemy can connect to Postgres."""
    app = Flask(__name__)
    init_app(app)
    return app


def main():
    """Collect streaming search data and write results to the database."""
    basicConfig(
        level=os.environ.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    search_field = os.environ.get('SEARCH_FIELD', 'name')
    search_value = os.environ.get('SEARCH_VALUE')
    if not search_value:
        log.error('SEARCH_VALUE environment variable is required')
        sys.exit(1)

    app = create_app()
    with app.app_context():
        db.create_all()
        log.info('Running search for %s=%r', search_field, search_value)
        results = search({'search_field': search_field, 'search_value': search_value})
        title_count = len(results.get('title_results', []))
        log.info('Search completed with %s title results', title_count)


if __name__ == '__main__':
    main()
