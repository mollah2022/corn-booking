import sys
import logging
import sentry_sdk
from datetime import datetime, timedelta, timezone

from app.db import session_scope
from app.sentry import init_sentry
from app.config.settings import BOOKING_API_BASE_URL, BOOKING_API_KEY
from app.api_client.booking_api_client import BookingApiClient
from app.repositories.booking_repository import BookingRepository
from app.services.booking_service import BookingService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("booking_cron")

init_sentry()


class BookingCron:
    """Cron job responsible for syncing booking data from the API App into the database."""

    def __init__(self, updated_from: str = None, updated_to: str = None):
        self.updated_from = updated_from
        self.updated_to = updated_to

        self.inserted_count = 0
        self.updated_count = 0
        self.failed_count = 0

    def _resolve_date_range(self):
        if not self.updated_to:
            self.updated_to = datetime.now(timezone.utc).isoformat()
        if not self.updated_from:
            self.updated_from = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    def _build_dependencies(self):
        self.api_client = BookingApiClient(
            base_url=BOOKING_API_BASE_URL,
            api_key=BOOKING_API_KEY,
        )
        self.booking_repository = BookingRepository()
        self.booking_service = BookingService(self.booking_repository)

    def _fetch_raw_bookings(self):
        logger.info(f"Fetching bookings updated_from={self.updated_from} updated_to={self.updated_to}")
        try:
            return self.api_client.fetch_bookings(self.updated_from, self.updated_to)
        except Exception:
            logger.exception("Failed to fetch bookings from API App")
            sentry_sdk.capture_exception()
            sentry_sdk.flush(timeout=5)
            sys.exit(1)

    def _process_bookings(self, session, raw_bookings: list):
        try:
            result = self.booking_service.save_all(session, raw_bookings)
            self.inserted_count = result["inserted"]
            self.updated_count = result["updated"]
        except Exception:
            self.failed_count = len(raw_bookings)
            logger.exception("Bulk processing failed")
            sentry_sdk.capture_exception()

    def _report(self):
        logger.info(
            f"Inserted {self.inserted_count} row. "
            f"Updated {self.updated_count} row. "
            f"Failed {self.failed_count} row."
        )

    def run(self):
        self._resolve_date_range()
        self._build_dependencies()
        raw_bookings = self._fetch_raw_bookings()

        with session_scope() as session:
            self._process_bookings(session, raw_bookings)

        self._report()


if __name__ == "__main__":
    arg_from = sys.argv[1] if len(sys.argv) > 1 else None
    arg_to = sys.argv[2] if len(sys.argv) > 2 else None
    BookingCron(arg_from, arg_to).run()
