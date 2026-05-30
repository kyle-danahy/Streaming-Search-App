"""Data collector module for the streaming search application."""
from datetime import datetime
import urllib.request
import json
from urllib.parse import urlencode
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object without binding to a Flask app yet.
db = SQLAlchemy()


def init_app(app):
    """Initialize the SQLAlchemy object with the Flask application."""
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///StreamingSearchApp.sqlite3')
    db.init_app(app)


class StreamingSearch(db.Model):
    """Define the database model that is used to store the search query."""
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    search_query = db.Column(db.String(200), nullable=False)

def write_results_to_db(data):
    """Helper function to write search results to the database."""
    search_query = json.dumps(data)
    new_search = StreamingSearch(search_query=search_query)
    db.session.add(new_search)
    db.session.commit()

def get_most_recent_search():
    """Helper function to get the most recent search query from the database."""
    return StreamingSearch.query.order_by(StreamingSearch.datetime.desc()).first()

def search(query):
    """Helper function to perform a search using the Watchmode API. Calls the API
    and then writes the results to the database."""
    api_key = 'Ueg5Sw7ZedERgV0pzRjKdPa30qCteVX9Iua6QtQc'
    search_field = query['search_field']
    search_value = query['search_value']

    params = {
        'apiKey': api_key,
        'search_field': search_field,
        'search_value': search_value
    }

    url = f'https://api.watchmode.com/v1/search/?{urlencode(params)}'

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        # print(data)
        write_results_to_db(data)
        return data
