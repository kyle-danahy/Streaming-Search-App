"""This module parses data collected by the data collector based on user selections."""
import json

_app = None


def init_app(app):
    """Initialize the data analyzer with the Flask application."""
    global _app
    _app = app


def parse_streaming_services(database_results, checked_boxes):
    """This function will parse the full list of results and return only the results
    that are available on the streaming services the user selected. If the user
    did not select any of the checkboxes, all results will be returned."""
    if not checked_boxes:
        return list(database_results)

    # TODO: make this return a bit prettier of a list.
    filtered_results = []
    for result in database_results:
        services = json.loads(result.available_streaming_services)
        if any(service in checked_boxes for service in services):
            filtered_results.append(result)

    return filtered_results
