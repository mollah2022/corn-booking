class TestFlightsCronResolveDateRange:

    def test_defaults_are_set_when_dates_missing(self, flights_cron_class):
        cron = flights_cron_class()
        cron._resolve_date_range()

        assert cron.updated_from is not None
        assert cron.updated_to is not None

    def test_provided_dates_are_preserved(self, flights_cron_class):
        cron = flights_cron_class(updated_from="2026-06-01", updated_to="2026-09-30")
        cron._resolve_date_range()

        assert cron.updated_from == "2026-06-01"
        assert cron.updated_to == "2026-09-30"


class TestFlightsCronRun:

    def test_run_completes_and_reports_zero_counts(self, flights_cron_class):
        cron = flights_cron_class("2026-06-01", "2026-09-30")
        cron.run()

        assert cron.inserted_count == 0
        assert cron.updated_count == 0
        assert cron.failed_count == 0
