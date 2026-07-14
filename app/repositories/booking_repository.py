from app.models.booking import Booking
from app.repositories.booking_repository_interface import BookingRepositoryInterface
from app.services.common_service import CommonService
from sqlalchemy.dialects.postgresql import insert as pg_insert

CHUNK_SIZE = 50

UPSERT_COLUMNS = [
    "conversion_key",
    "property_id",
    "referral_property_id",
    "status",
    "travel_purpose",
    "country_code",
    "region",
    "currency",
    "check_in_date",
    "check_out_date",
    "site_key",
    "device",
    "total_price",
    "revenue_usd",
]


class BookingRepository(BookingRepositoryInterface):

    def find_by_transaction_id(self, session, transaction_id: str):
        return session.query(Booking).filter_by(transaction_id=transaction_id).first()

    def bulk_save(self, session, records: list) -> dict:
        inserted_count = 0
        updated_count = 0

        for chunk in CommonService.chunk_list(records, CHUNK_SIZE):
            transaction_ids = [r["transaction_id"] for r in chunk]

            existing_ids = {
                row.transaction_id
                for row in session.query(Booking.transaction_id)
                .filter(Booking.transaction_id.in_(transaction_ids))
                .all()
            }

            stmt = pg_insert(Booking).values(chunk)
            update_dict = {col: getattr(stmt.excluded, col) for col in UPSERT_COLUMNS}
            stmt = stmt.on_conflict_do_update(
                index_elements=["transaction_id"],
                set_=update_dict,
            )

            session.execute(stmt)

            for record in chunk:
                if record["transaction_id"] in existing_ids:
                    updated_count += 1
                else:
                    inserted_count += 1

        return {"inserted": inserted_count, "updated": updated_count}
