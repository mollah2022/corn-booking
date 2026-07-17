import sys
import logging
from datetime import datetime, timedelta, timezone

from app.db import session_scope
from app.config.settings import BOOKING_API_BASE_URL, BOOKING_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("flights_cron")


class FlightsCron:
    """Cron job responsible for syncing flight data - placeholder example
    showing how a new job follows the exact same structure as BookingCron."""

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

    def _report(self):
        logger.info(
            f"Inserted {self.inserted_count} row. "
            f"Updated {self.updated_count} row. "
            f"Failed {self.failed_count} row."
        )

    def run(self):
        self._resolve_date_range()
        logger.info(f"Flights sync placeholder ran for {self.updated_from} to {self.updated_to}")
        self._report()
