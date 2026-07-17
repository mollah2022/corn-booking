from app.repositories.booking_repository_interface import BookingRepositoryInterface


class _DummyRepository(BookingRepositoryInterface):
    """Minimal concrete subclass that calls super() to execute each abstract method's body."""

    def find_by_transaction_id(self, session, transaction_id: str):
        return super().find_by_transaction_id(session, transaction_id)

    def bulk_save(self, session, records: list) -> dict:
        return super().bulk_save(session, records)


class TestBookingRepositoryInterface:

    def test_find_by_transaction_id_body_is_a_noop(self):
        repo = _DummyRepository()
        result = repo.find_by_transaction_id(session=None, transaction_id="txn-1")
        assert result is None

    def test_bulk_save_body_is_a_noop(self):
        repo = _DummyRepository()
        result = repo.bulk_save(session=None, records=[])
        assert result is None
