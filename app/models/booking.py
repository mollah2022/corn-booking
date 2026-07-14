from app import db
from datetime import datetime


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    conversion_key = db.Column(db.String(255))
    property_id = db.Column(db.String(64))
    referral_property_id = db.Column(db.String(64))

    status = db.Column(db.String(32))

    travel_purpose = db.Column(db.String(32))
    country_code = db.Column(db.String(8))
    region = db.Column(db.String(64))

    currency = db.Column(db.String(8))

    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)

    site_key = db.Column(db.String(16))
    device = db.Column(db.String(16))

    total_price = db.Column(db.Numeric(12, 2))
    revenue_usd = db.Column(db.Numeric(12, 2))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)