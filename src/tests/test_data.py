"""Class that houses pre defined data for unit testing"""

class TestData:
    """Canned data for unit testing"""

    @staticmethod
    def get_sample_search_results():
        """Returns a sample search result from the Watchmode API."""
        return {
            "title_results": [
                {
                    "id": 1,
                    "name": "Breaking Bad",
                    "type": "movie",
                    "available_streaming_services": ["Netflix", "Hulu"]
                },
                {
                    "id": 2,
                    "name": "The Office",
                    "type": "show",
                    "available_streaming_services": ["Peacock", "Amazon Prime"]
                }
            ]
        }
