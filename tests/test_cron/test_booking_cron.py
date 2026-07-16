class TestResolveDateRange:

    def test_defaults_are_set_when_dates_missing(self, booking_cron_class):
        cron = booking_cron_class()
        cron._resolve_date_range()

        assert cron.updated_from is not None
        assert cron.updated_to is not None

    def test_provided_dates_are_preserved(self, booking_cron_class):
        cron = booking_cron_class(updated_from="2026-06-01", updated_to="2026-09-30")
        cron._resolve_date_range()

        assert cron.updated_from == "2026-06-01"
        assert cron.updated_to == "2026-09-30"


class TestFetchRawBookings:

    def test_returns_bookings_on_success(self, booking_cron_class, mock_cron_dependencies, sample_booking_raw):
        mock_cron_dependencies["api_client"].fetch_bookings.return_value = [sample_booking_raw]

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron._build_dependencies()
        result = cron._fetch_raw_bookings()

        assert result == [sample_booking_raw]

    def test_exits_process_on_api_failure(self, booking_cron_class, mock_cron_dependencies):
        mock_cron_dependencies["api_client"].fetch_bookings.side_effect = ConnectionError("api down")

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron._build_dependencies()

        import pytest
        with pytest.raises(SystemExit) as exc_info:
            cron._fetch_raw_bookings()

        assert exc_info.value.code == 1


class TestProcessBookings:

    def test_updates_counts_on_success(self, booking_cron_class, mock_cron_dependencies, sample_booking_raw):
        mock_cron_dependencies["service"].save_all.return_value = {"inserted": 3, "updated": 2}

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron._build_dependencies()
        cron._process_bookings(mock_cron_dependencies["session"], [sample_booking_raw])

        assert cron.inserted_count == 3
        assert cron.updated_count == 2
        assert cron.failed_count == 0

    def test_sets_failed_count_on_exception(self, booking_cron_class, mock_cron_dependencies, sample_booking_raw):
        mock_cron_dependencies["service"].save_all.side_effect = Exception("db error")

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron._build_dependencies()
        cron._process_bookings(mock_cron_dependencies["session"], [sample_booking_raw, sample_booking_raw])

        assert cron.failed_count == 2
        assert cron.inserted_count == 0
        assert cron.updated_count == 0


class TestRun:

    def test_run_executes_full_flow_and_sets_final_counts(
        self, booking_cron_class, mock_cron_dependencies, sample_booking_raw
    ):
        mock_cron_dependencies["api_client"].fetch_bookings.return_value = [sample_booking_raw]
        mock_cron_dependencies["service"].save_all.return_value = {"inserted": 1, "updated": 0}

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron.run()

        assert cron.inserted_count == 1
        assert cron.updated_count == 0
        assert cron.failed_count == 0

    def test_run_uses_session_scope_as_context_manager(
        self, booking_cron_class, mock_cron_dependencies, sample_booking_raw
    ):
        mock_cron_dependencies["api_client"].fetch_bookings.return_value = [sample_booking_raw]
        mock_cron_dependencies["service"].save_all.return_value = {"inserted": 1, "updated": 0}

        cron = booking_cron_class("2026-06-01", "2026-09-30")
        cron.run()

        mock_cron_dependencies["service"].save_all.assert_called_once_with(
            mock_cron_dependencies["session"], [sample_booking_raw]
        )
