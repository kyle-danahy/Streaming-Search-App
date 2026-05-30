"""This class will take the data collected by the data collector
and format it into a more human readable format. It also will
clean up any not so relevant results."""
from src.data_collector.data_collector import get_most_recent_search

class DataAnalyzer:
    """Provides methods to clean and filter the raw query data based on user selections"""
    def __init__(self, data):
        self.data = get_most_recent_search().search_query

    def clean_data(self):
        """This function will take the raw data from the data collector and
        format it into a more human readable format. It will also clean up
        any not so relevant results."""
        # For now, we will just return the raw data. In the future, we can
        # add more functionality to this function to clean up the data and
        # make it more human readable.
        filtered_data = self.filter_data(self.data)
        return filtered_data

    def filter_data(self, filter_criteria):
        """This function will filter data, primarily removing results that
        are not on the streaming service that the user selected or results that do
        not match the users selections for type of content (movie, show, etc)."""
        if filter_criteria:
            parse_streaming_services = filter_criteria.get("streaming_services", [])
            parse_content_types = filter_criteria.get("content_types", [])

        return self.data
