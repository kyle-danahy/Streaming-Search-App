#!/usr/bin/env python3
"""A simple Flask app that echoes user input back to the user."""

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
         <input name="movie_show_title" type="text" placeholder="Movie or Show Title">
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/query_streaming_api", methods=["POST"])
def query_streaming_api():
    """Queries the streaming API with the user's input."""
    movie_show_title = request.form.get("movie_show_title", "")
    data_collector.search({"search_field": "name", "search_value": movie_show_title})
    db_results = data_collector.get_most_recent_search()
    # print("db_results.search_query:", str(db_results.search_query))
    # print("db_results.results:", str(db_results.results))
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
                        for result in db_results.results
                    )
                }
            </table>
        </div>
        '''

if __name__ == "__main__":
    app.run(debug=True)
