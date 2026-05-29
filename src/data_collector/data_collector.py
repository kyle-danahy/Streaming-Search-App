"""Data collector module for the streaming search application."""
from datetime import datetime
import urllib.request
import json
from urllib.parse import urlencode
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///StreamingSearchApp.sqlite3'

db = SQLAlchemy(app)


class StreamingSearch(db.Model):
    """Define the database model that is used to store the search query."""
    datetime = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    search_query = db.Column(db.String(200), nullable=False)

def search(query):
    """Helper function to perform a search using the Watchmode API."""
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
        print(data)
