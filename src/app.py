#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

import json
import time
from logging import getLogger, log

from flask import Flask, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.data_analyzer import data_analyzer
from src.data_collector import data_collector
from src.database.database_helper import (
    clear_database,
    consume_api_results_to_db,
    db,
    get_individual_results_by_ids,
    get_most_recent_search,
    init_app,
)
from src.monitoring.metrics import (
    search_duration_seconds,
    search_requests_total,
    search_results_returned,
    search_title_results,
)

log = getLogger(__name__)

app = Flask(__name__)
init_app(app)

@app.route("/")
def main():
    """Main page with a form to submit user input."""
    return '''
     <form action="/query_streaming_api" method="POST">
         <input name="movie_show_title" type="text" placeholder="Movie or Show Title">
         <input type="submit" value="Submit!">
         <p>Select the streaming services you want to see results for:</p>
         <table>
            <tr>
                <td><label><input type="checkbox" name="streaming_service" value="Netflix"> Netflix</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Hulu"> Hulu</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Prime Video"> Prime Video</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Disney+"> Disney+</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Apple TV+"> Apple TV+</label></td>
            </tr>
            <tr>
                <td><label><input type="checkbox" name="streaming_service" value="Peacock"> Peacock</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Paramount+"> Paramount+</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="HBO Max"> HBO Max</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Showtime"> Showtime</label></td>
                <td><label><input type="checkbox" name="streaming_service" value="Starz"> Starz</label></td>
            </tr>
         </table>
     </form>
     <form>
        <button onclick="window.open('https://streaming-search-grafana-ce17a8229c97.herokuapp.com/public-dashboards/e75312c18d414025997adee8da827ffd', '_blank')">
            View Metrics on Grafana
        </button>
     </form>
     '''

@app.route("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route("/query_streaming_api", methods=["POST"])
def query_streaming_api():
    """Queries the streaming API with the user's input."""
    start_time = time.perf_counter()
    status = 'success'
    movie_show_title = request.form.get("movie_show_title", "")

    try:
        clear_database()

        data_collector.search({"search_field": "name", "search_value": movie_show_title})
        consume_api_results_to_db()
        db_results = get_most_recent_search()
        title_results = []
        if db_results and db_results.search_query:
            title_results = json.loads(db_results.search_query).get("title_results", [])

        search_title_results.observe(len(title_results))

        ids = [result.get('id') for result in title_results]
        log.info("Pulling %s individual results from database...", len(ids))
        if ids:
            database_results = get_individual_results_by_ids(ids)
            checked_boxes = request.form.getlist("streaming_service")
            results = data_analyzer.parse_streaming_services(database_results, checked_boxes)
        else:
            results = []

        search_results_returned.observe(len(results))

        return f'''
        <div>
            <style>
                table {{
                    border-collapse: collapse;
                }}
                table, th, td {{
                    border: 1px solid black;
                }}
            </style>
            <p>You entered: {movie_show_title}</p>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Available Streaming Services</th>
                </tr>
                {''.join(f"<tr>"
                            f"<td>{result.result_name}</td>"
                            f"<td>{result.result_type}</td>"
                            f"<td>{result.available_streaming_services}</td>"
                        f"</tr>"
                        for result in results
                    )
                }
            </table>
            <button onclick="window.location.href='/'">Go Back</button>
            <form>
                <button onclick="window.open('https://streaming-search-grafana-ce17a8229c97.herokuapp.com/public-dashboards/e75312c18d414025997adee8da827ffd', '_blank')">
                    View Metrics on Grafana
                </button>
            </form>
        </div>
        '''
    except Exception:
        status = 'error'
        raise
    finally:
        search_duration_seconds.observe(time.perf_counter() - start_time)
        search_requests_total.labels(status=status).inc()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
