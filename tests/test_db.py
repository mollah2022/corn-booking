from app.db import session_scope
from app.models.booking import Booking


class TestSessionScope:

    def test_commits_on_success(self, real_session_scope):
        with session_scope() as session:
            booking = Booking(
                transaction_id="db-test-001",
                status="pending",
                region="Europe",
            )
            session.add(booking)

        with session_scope() as verify_session:
            result = verify_session.query(Booking).filter_by(transaction_id="db-test-001").first()
            assert result is not None

    def test_rolls_back_on_exception(self, real_session_scope):
        try:
            with session_scope() as session:
                booking = Booking(
                    transaction_id="db-test-002",
                    status="pending",
                    region="Europe",
                )
                session.add(booking)
                raise ValueError("simulated failure")
        except ValueError:
            pass

        with session_scope() as verify_session:
            result = verify_session.query(Booking).filter_by(transaction_id="db-test-002").first()
            assert result is None
