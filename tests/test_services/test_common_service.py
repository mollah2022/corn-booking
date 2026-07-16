import pytest
from unittest.mock import patch, MagicMock


class TestGetRegion:

    def test_known_country_returns_correct_region(self, common_service):
        assert common_service.get_region("DE") == "Europe"

    def test_lowercase_country_code_is_normalized(self, common_service):
        assert common_service.get_region("de") == "Europe"

    def test_unknown_country_returns_other(self, common_service):
        assert common_service.get_region("ZZ") == "other"

    def test_none_country_returns_none(self, common_service):
        assert common_service.get_region(None) is None

    def test_empty_string_country_returns_none(self, common_service):
        assert common_service.get_region("") is None


class TestMapStatus:

    def test_known_status_is_normalized(self, common_service):
        assert common_service.map_status("booked") == "pending"

    def test_stayed_maps_to_approved(self, common_service):
        assert common_service.map_status("stayed") == "approved"

    def test_cancelled_variants_map_to_cancelled(self, common_service):
        assert common_service.map_status("cancelled_by_hotel") == "cancelled"
        assert common_service.map_status("cancelled_by_guest") == "cancelled"
        assert common_service.map_status("no_show") == "cancelled"

    def test_unknown_status_returns_as_is(self, common_service):
        assert common_service.map_status("some_unknown_status") == "some_unknown_status"


class TestParseLabel:

    def test_parses_site_key_device_and_property_id(self, common_service):
        label = "k-htl_d-m_u-abc123_g-xyz_t-gp_p-BC-483720"
        result = common_service.parse_label(label)

        assert result["site_key"] == "HTL"
        assert result["device"] == "mobile"
        assert result["referral_property_id"] == "BC-483720"

    def test_desktop_device_code(self, common_service):
        label = "k-htl_d-d_p-BC-100"
        result = common_service.parse_label(label)
        assert result["device"] == "desktop"

    def test_tablet_device_code(self, common_service):
        label = "k-htl_d-t_p-BC-100"
        result = common_service.parse_label(label)
        assert result["device"] == "tablet"

    def test_empty_label_returns_empty_dict(self, common_service):
        result = common_service.parse_label("")
        assert result == {}

    def test_unrecognized_device_code_passed_through(self, common_service):
        label = "k-htl_d-x_p-BC-100"
        result = common_service.parse_label(label)
        assert result["device"] == "x"


class TestChunkList:

    def test_splits_into_correct_number_of_chunks(self, common_service):
        records = list(range(10))
        chunks = list(common_service.chunk_list(records, 3))
        assert len(chunks) == 4

    def test_chunk_sizes_are_correct(self, common_service):
        records = list(range(10))
        chunks = list(common_service.chunk_list(records, 3))
        assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    def test_empty_list_returns_no_chunks(self, common_service):
        chunks = list(common_service.chunk_list([], 5))
        assert chunks == []

    def test_chunk_size_larger_than_list(self, common_service):
        records = [1, 2, 3]
        chunks = list(common_service.chunk_list(records, 10))
        assert chunks == [[1, 2, 3]]


class TestGetExchangeRate:
    """External API call is mocked - we never hit the real exchangerate-api.com in tests."""

    @patch("app.services.common_service.requests.get")
    def test_returns_correct_rate_from_api_response(self, mock_get, common_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"USD": 1.08}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rate = common_service.get_exchange_rate("EUR", "USD")

        assert rate == 1.08
        mock_get.assert_called_once()

    @patch("app.services.common_service.requests.get")
    def test_missing_target_currency_returns_none(self, mock_get, common_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"GBP": 0.85}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rate = common_service.get_exchange_rate("EUR", "USD")

        assert rate is None

    @patch("app.services.common_service.requests.get")
    def test_http_error_propagates(self, mock_get, common_service):
        import requests
        mock_get.side_effect = requests.exceptions.HTTPError("API down")

        with pytest.raises(requests.exceptions.HTTPError):
            common_service.get_exchange_rate("EUR", "USD")
