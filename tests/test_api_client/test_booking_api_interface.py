from app.api_client.booking_api_interface import BookingApiInterface


class _DummyClient(BookingApiInterface):
    """Minimal concrete subclass that calls super() to execute the abstract method's body."""

    def fetch_bookings(self, updated_from: str, updated_to: str) -> list:
        return super().fetch_bookings(updated_from, updated_to)


class TestBookingApiInterface:

    def test_abstract_method_body_is_a_noop(self):
        client = _DummyClient()
        result = client.fetch_bookings("2026-06-01", "2026-09-30")
        assert result is None
