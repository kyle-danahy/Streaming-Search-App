CREATE TABLE IF NOT EXISTS streaming_search (
    datetime TIMESTAMP PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
    search_query TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS individual_result (
    id SERIAL PRIMARY KEY,
    search_datetime TIMESTAMP NOT NULL,
    result_id INTEGER NOT NULL,
    result_name TEXT NOT NULL,
    result_type TEXT NOT NULL,
    available_streaming_services TEXT NOT NULL,
    FOREIGN KEY (search_datetime) REFERENCES streaming_search(datetime)
);
