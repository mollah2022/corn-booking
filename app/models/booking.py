from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from app.db import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(String(64), unique=True, nullable=False)
    conversion_key = Column(String(255))
    property_id = Column(String(64))
    referral_property_id = Column(String(64))

    status = Column(String(32))

    travel_purpose = Column(String(32))
    country_code = Column(String(8))
    region = Column(String(64))

    currency = Column(String(8))

    check_in_date = Column(Date)
    check_out_date = Column(Date)

    site_key = Column(String(16))
    device = Column(String(16))

    total_price = Column(Numeric(12, 2))
    revenue_usd = Column(Numeric(12, 2))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
