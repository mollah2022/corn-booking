from unittest.mock import patch


class TestTransform:

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_transform_maps_all_fields_correctly(self, mock_rate, booking_service, sample_booking_raw):
        mock_rate.return_value = 1.08

        result = booking_service.transform(sample_booking_raw)

        assert result["transaction_id"] == "7843159201"
        assert result["conversion_key"] == sample_booking_raw["label"]
        assert result["property_id"] == "BC-782114"
        assert result["referral_property_id"] == "BC-483720"
        assert result["status"] == "pending"
        assert result["travel_purpose"] == "leisure"
        assert result["country_code"] == "DE"
        assert result["region"] == "Europe"
        assert result["currency"] == "EUR"
        assert result["check_in_date"] == "2026-09-15"
        assert result["check_out_date"] == "2026-09-18"
        assert result["site_key"] == "HTL"
        assert result["device"] == "mobile"
        assert result["total_price"] == 186.75

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_transform_calculates_revenue_usd_correctly(self, mock_rate, booking_service, sample_booking_raw):
        mock_rate.return_value = 1.08

        result = booking_service.transform(sample_booking_raw)

        assert result["revenue_usd"] == 201.69

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_transform_handles_none_nested_fields_without_crashing(
        self, mock_rate, booking_service, sample_booking_raw_missing_fields
    ):
        mock_rate.return_value = 1.08

        result = booking_service.transform(sample_booking_raw_missing_fields)

        assert result["transaction_id"] is None
        assert result["property_id"] is None
        assert result["total_price"] is None
        assert result["revenue_usd"] is None
        assert result["country_code"] == ""
        assert result["region"] is None

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_transform_skips_revenue_calc_when_rate_unavailable(self, mock_rate, booking_service, sample_booking_raw):
        mock_rate.return_value = None

        result = booking_service.transform(sample_booking_raw)

        assert result["revenue_usd"] is None


class TestRateCaching:

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_exchange_rate_is_cached_after_first_call(self, mock_rate, booking_service, sample_booking_raw):
        mock_rate.return_value = 1.08

        booking_service.transform(sample_booking_raw)
        booking_service.transform(sample_booking_raw)
        booking_service.transform(sample_booking_raw)

        assert mock_rate.call_count == 1

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_different_currencies_trigger_separate_calls(self, mock_rate, booking_service, sample_booking_raw):
        mock_rate.return_value = 1.08

        booking_service.transform(sample_booking_raw)

        second_booking = dict(sample_booking_raw)
        second_booking["currencies"] = {"booker": "USD", "product": "USD"}
        booking_service.transform(second_booking)

        assert mock_rate.call_count == 2


class TestSaveAll:

    @patch("app.services.common_service.CommonService.get_exchange_rate")
    def test_save_all_transforms_and_delegates_to_repository(
        self, mock_rate, booking_service, mock_booking_repository, sample_booking_raw
    ):
        mock_rate.return_value = 1.08
        mock_booking_repository.bulk_save.return_value = {"inserted": 1, "updated": 0}

        fake_session = "fake_session_object"
        result = booking_service.save_all(fake_session, [sample_booking_raw])

        mock_booking_repository.bulk_save.assert_called_once()
        called_session, called_records = mock_booking_repository.bulk_save.call_args[0]
        assert called_session == fake_session
        assert len(called_records) == 1
        assert called_records[0]["transaction_id"] == "7843159201"
        assert result == {"inserted": 1, "updated": 0}
