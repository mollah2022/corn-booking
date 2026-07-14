from app import db
from app.models.booking import Booking
from app.repositories.booking_repository_interface import BookingRepositoryInterface


class BookingRepository(BookingRepositoryInterface):

    def find_by_transaction_id(self, transaction_id: str):
        return Booking.query.filter_by(transaction_id=transaction_id).first()

    def insert(self, booking_data: dict):
        booking = Booking(**booking_data)
        db.session.add(booking)
        db.session.commit()
        return booking

    def update(self, booking, booking_data: dict):
        for key, value in booking_data.items():
            setattr(booking, key, value)
        db.session.commit()
        return booking