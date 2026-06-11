"""Unit tests for the data analyzer module."""

import json
from unittest.mock import Mock, patch

import pytest

from src.data_analyzer import data_analyzer
from src.tests.test_data import TestData


@pytest.fixture
def analyzer():
    """Provide the data analyzer module for testing."""
    return data_analyzer


def _mock_individual_result(name, result_type, services):
    """Build a mock IndividualResult as stored by the data collector."""
    result = Mock()
    result.result_name = name
    result.result_type = result_type
    result.available_streaming_services = json.dumps(services)
    return result


@pytest.fixture
def sample_individual_results():
    """Mock database rows returned after a search."""
    return [
        _mock_individual_result('Breaking Bad', 'movie', ['Netflix', 'Hulu']),
        _mock_individual_result('The Office', 'show', ['Peacock', 'Amazon Prime']),
        _mock_individual_result('Stranger Things', 'show', ['Netflix']),
    ]


class TestParseStreamingServices:
    """Test suite for parse_streaming_services()."""

    def test_returns_all_results_when_no_services_selected(
        self, analyzer, sample_individual_results
    ):
        """When no checkboxes are selected, every result should be returned."""
        results = analyzer.parse_streaming_services(sample_individual_results, [])

        assert len(results) == 3
        assert results == sample_individual_results

    def test_filters_results_by_single_streaming_service(
        self, analyzer, sample_individual_results
    ):
        """Only results available on the selected service should be returned."""
        results = analyzer.parse_streaming_services(sample_individual_results, ['Netflix'])

        assert len(results) == 2
        assert {result.result_name for result in results} == {
            'Breaking Bad',
            'Stranger Things',
        }

    def test_filters_results_by_multiple_streaming_services(
        self, analyzer, sample_individual_results
    ):
        """Results matching any selected service should be included."""
        results = analyzer.parse_streaming_services(
            sample_individual_results,
            ['Hulu', 'Peacock'],
        )

        assert len(results) == 2
        assert {result.result_name for result in results} == {'Breaking Bad', 'The Office'}

    def test_returns_empty_list_when_no_results_match(
        self, analyzer, sample_individual_results
    ):
        """When no results match the selected services, an empty list is returned."""
        results = analyzer.parse_streaming_services(sample_individual_results, ['Showtime'])

        assert results == []
