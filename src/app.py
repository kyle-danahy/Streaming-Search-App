#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

import json
from logging import getLogger, log
from flask import Flask, request

from src.data_analyzer import data_analyzer
from src.data_collector import data_collector
from src.database.database_helper import clear_database

log = getLogger(__name__)

app = Flask(__name__)
data_collector.init_app(app)

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
     '''

@app.route("/query_streaming_api", methods=["POST"])
def query_streaming_api():
    """Queries the streaming API with the user's input."""
    movie_show_title = request.form.get("movie_show_title", "")
    clear_database(
        data_collector.db,
        data_collector.IndividualResult,
        data_collector.StreamingSearch
    )

    data_collector.search({"search_field": "name", "search_value": movie_show_title})
    db_results = data_collector.get_most_recent_search()
    title_results = []
    if db_results and db_results.search_query:
        title_results = json.loads(db_results.search_query).get("title_results", [])

    ids = [result.get('id') for result in title_results]
    log.info("Pulling %s individual results from database...", len(ids))
    if ids:
        database_results = data_collector.IndividualResult.query.filter(
            data_collector.IndividualResult.result_id.in_(ids)
        ).all()
        # Create a list of all streaming services the user checked a box for.
        checked_boxes = request.form.getlist("streaming_service")
        
        # Parse the full list of results and only return results that are available on a
        # streaming service the user checked a box for.
        results = data_analyzer.parse_streaming_services(database_results, checked_boxes)
    else:
        results = []

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
        </div>
        '''

if __name__ == "__main__":
    with app.app_context():
        data_collector.db.create_all()
    app.run(debug=True)
