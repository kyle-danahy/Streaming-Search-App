"""Run the data collector as a standalone process inside Docker."""
import os
import sys
from logging import basicConfig, getLogger

from flask import Flask

from src.data_collector.data_collector import db, init_app, search

log = getLogger(__name__)


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
