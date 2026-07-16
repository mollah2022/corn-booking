import pytest
import requests
from unittest.mock import patch, MagicMock



class TestFetchBookingsSuccess:

    @patch("app.api_client.booking_api_client.requests.get")
    def test_returns_results_list_from_response(self, mock_get, api_client, sample_booking_raw):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": [sample_booking_raw]}
        mock_get.return_value = mock_response

        result = api_client.fetch_bookings("2026-06-01", "2026-09-30")

        assert result == [sample_booking_raw]

    @patch("app.api_client.booking_api_client.requests.get")
    def test_returns_empty_list_when_no_results_key(self, mock_get, api_client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = api_client.fetch_bookings("2026-06-01", "2026-09-30")

        assert result == []

    @patch("app.api_client.booking_api_client.requests.get")
    def test_sends_correct_url_and_params(self, mock_get, api_client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        api_client.fetch_bookings("2026-06-01", "2026-09-30")

        called_url = mock_get.call_args[0][0]
        called_params = mock_get.call_args[1]["params"]

        assert called_url == "http://localhost:5001/bookings"
        assert called_params == {"updated_from": "2026-06-01", "updated_to": "2026-09-30"}


class TestFetchBookingsAuth:

    @patch("app.api_client.booking_api_client.requests.get")
    def test_no_auth_header_when_api_key_missing(self, mock_get, api_client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        api_client.fetch_bookings("2026-06-01", "2026-09-30")

        called_headers = mock_get.call_args[1]["headers"]
        assert "Authorization" not in called_headers

    @patch("app.api_client.booking_api_client.requests.get")
    def test_auth_header_included_when_api_key_present(self, mock_get, api_client_with_key):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        api_client_with_key.fetch_bookings("2026-06-01", "2026-09-30")

        called_headers = mock_get.call_args[1]["headers"]
        assert called_headers["Authorization"] == "Bearer secret-key-123"


class TestFetchBookingsRetry:
    """The client retries up to 3 times with exponential backoff before giving up."""

    @patch("app.api_client.booking_api_client.requests.get")
    def test_retries_on_connection_error_then_succeeds(self, mock_get, api_client):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}

        mock_get.side_effect = [
            requests.exceptions.ConnectionError("connection refused"),
            requests.exceptions.ConnectionError("connection refused"),
            mock_response,
        ]

        result = api_client.fetch_bookings("2026-06-01", "2026-09-30")

        assert result == []
        assert mock_get.call_count == 3

    @patch("app.api_client.booking_api_client.requests.get")
    def test_raises_after_exhausting_all_retries(self, mock_get, api_client):
        mock_get.side_effect = requests.exceptions.ConnectionError("connection refused")

        with pytest.raises(requests.exceptions.ConnectionError):
            api_client.fetch_bookings("2026-06-01", "2026-09-30")

        assert mock_get.call_count == 3

    @patch("app.api_client.booking_api_client.requests.get")
    def test_raises_immediately_on_http_error_status(self, mock_get, api_client):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            api_client.fetch_bookings("2026-06-01", "2026-09-30")
