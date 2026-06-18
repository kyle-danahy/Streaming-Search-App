"""Prometheus metrics for the streaming search application."""

from prometheus_client import Counter, Histogram

search_requests_total = Counter(
    'streaming_search_requests_total',
    'Total streaming search requests processed.',
    ['status'],
)

search_results_returned = Histogram(
    'streaming_search_results_returned',
    'Filtered results returned to the user per search.',
    buckets=(0, 1, 2, 5, 10, 20, 50),
)

search_title_results = Histogram(
    'streaming_search_title_results',
    'Title matches returned by the Watchmode API per search.',
    buckets=(0, 1, 2, 5, 10, 20, 50, 100),
)

search_duration_seconds = Histogram(
    'streaming_search_duration_seconds',
    'Time spent processing a streaming search request.',
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)
