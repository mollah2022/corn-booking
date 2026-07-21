from unittest.mock import patch


class TestInitSentry:

    @patch("app.sentry.sentry_sdk.init")
    @patch("app.sentry.SENTRY_DSN", None)
    def test_does_nothing_when_dsn_not_set(self, mock_sentry_init):
        from app.sentry import init_sentry
        init_sentry()
        mock_sentry_init.assert_not_called()

    @patch("app.sentry.sentry_sdk.init")
    @patch("app.sentry.SENTRY_DSN", "https://fake-dsn@sentry.io/123")
    @patch("app.sentry.SENTRY_ENVIRONMENT", "testing")
    def test_initializes_sentry_when_dsn_is_set(self, mock_sentry_init):
        from app.sentry import init_sentry
        init_sentry()

        mock_sentry_init.assert_called_once()
        call_kwargs = mock_sentry_init.call_args[1]
        assert call_kwargs["dsn"] == "https://fake-dsn@sentry.io/123"
        assert call_kwargs["environment"] == "testing"
