#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

import json

from flask import Flask, request

from src.data_collector import data_collector

app = Flask(__name__)
data_collector.init_app(app)

with app.app_context():
    data_collector.db.create_all()

@app.route("/")
def main():
    """Main page with a form to submit user input."""
    return '''
     <form action="/query_streaming_api" method="POST">
         <input name="movie_show_title" type="text" placeholder="Enter a movie or show title">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/query_streaming_api", methods=["POST"])
def query_streaming_api():
    """Queries the streaming API with the user's input."""
    movie_show_title = request.form.get("movie_show_title", "")
    # Here you would call your data collector function with the user's input
    data_collector.search({"search_field": "name", "search_value": movie_show_title})
    db_results = data_collector.StreamingSearch.query.all()
    return "You entered: " + movie_show_title + " - results from the database: " + json.dumps(db_results)

if __name__ == "__main__":
    app.run(debug=True)
