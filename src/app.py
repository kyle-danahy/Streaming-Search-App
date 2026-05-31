#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

import json
from flask import Flask, request

from src.data_collector import data_collector

app = Flask(__name__)
data_collector.init_app(app)

with app.app_context():
    data_collector.db.create_all()

# Would not normally do this in production but implementing this as a simple cleanup function
# In a "real" app I would add some checks to see if the record exists in the DB before writing
# and maybe have a periodic cleanup to prevent the table from getting too cluttered
def clear_database():
    """Clear the search and individual result tables before a new API query."""
    data_collector.db.session.query(data_collector.IndividualResult).delete()
    data_collector.db.session.query(data_collector.StreamingSearch).delete()
    data_collector.db.session.commit()


@app.route("/")
def main():
    """Main page with a form to submit user input."""
    return '''
     <form action="/query_streaming_api" method="POST">
         <input name="movie_show_title" type="text" placeholder="Movie or Show Title">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/query_streaming_api", methods=["POST"])
def query_streaming_api():
    """Queries the streaming API with the user's input."""
    movie_show_title = request.form.get("movie_show_title", "")
    clear_database()
    data_collector.search({"search_field": "name", "search_value": movie_show_title})
    db_results = data_collector.get_most_recent_search()
    title_results = []
    if db_results and db_results.search_query:
        title_results = json.loads(db_results.search_query).get("title_results", [])        

    ids = [result.get('id') for result in title_results]
    print(f"Pulling {len(ids)} individual results from database...")
    if ids:
        individual_results = data_collector.IndividualResult.query.filter(
            data_collector.IndividualResult.result_id.in_(ids)
        ).all()
    else:
        individual_results = []

    return f'''
        <div>
            <p>You entered: {movie_show_title}</p>
            <p>query successful?: {db_results.search_query is not None}</p>
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
                        for result in individual_results
                    )
                }
            </table>
            <button onclick="window.location.href='/'">Go Back</button>
        </div>
        '''

if __name__ == "__main__":
    app.run(debug=True)
