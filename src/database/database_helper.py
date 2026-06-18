#!/usr/bin/env python3
import os
from pathlib import Path
from logging import getLogger, log
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

if not os.environ.get('DYNO'):
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parents[2] / '.env')
    except ImportError:
        pass

LOCAL_DATABASE_URL = (
    'postgresql://flaskuser:flaskpass@localhost:5432/flaskdb'
)

db = SQLAlchemy()
log = getLogger(__name__)

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

def get_database_uri():
    """Return the database URI for SQLAlchemy.

    Priority order:
    1. environment variable SQLALCHEMY_DATABASE_URI / DATABASE_URL
    2. Docker/local Postgres defaults from POSTGRES_* environment variables
    """
    configured_uri = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    if configured_uri:
        return configured_uri.replace('postgres://', 'postgresql://', 1)

    postgres_user = os.environ.get('POSTGRES_USER', 'flaskuser')
    postgres_password = os.environ.get('POSTGRES_PASSWORD', 'flaskpass')
    postgres_db = os.environ.get('POSTGRES_DB', 'flaskdb')
    postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
    postgres_port = os.environ.get('POSTGRES_PORT', '5432')

    return (
        f'postgresql://{postgres_user}:{postgres_password}'
        f'@{postgres_host}:{postgres_port}/{postgres_db}'
    )

def init_app(app):
    """Initialize SQLAlchemy with the Flask application."""
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', get_database_uri())
    db.init_app(app)

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
    from src.data_collector.data_collector import get_available_streaming_services

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

def get_individual_results_by_ids(result_ids):
    """Return individual result rows matching the given result IDs."""
    if not result_ids:
        return []
    return IndividualResult.query.filter(
        IndividualResult.result_id.in_(result_ids)
    ).all()

"""Would not normally do this in production but implementing this as a simple cleanup function
In a "real" app I would add some checks to see if the record exists in the DB before writing
and maybe have a periodic cleanup to prevent the table from getting too cluttered"""
def clear_database():
    """Clear the search and individual result tables before a new API query."""
    db.session.query(IndividualResult).delete()
    db.session.query(StreamingSearch).delete()
    db.session.commit()
