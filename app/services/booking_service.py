from app.services.common_service import CommonService


class BookingService:

    def __init__(self, booking_repository):
        self.booking_repository = booking_repository
        self._rate_cache = {}
        self.common_service = CommonService()

    def _get_cached_rate(self, currency: str) -> float:
        if currency not in self._rate_cache:
            self._rate_cache[currency] = self.common_service.get_exchange_rate(currency, "USD")
        return self._rate_cache[currency]

    def transform(self, raw_data: dict) -> dict:
        accommodations = raw_data.get("accommodations") or {}
        booker = raw_data.get("booker") or {}
        currencies = raw_data.get("currencies") or {}
        price = raw_data.get("price") or {}
        acc_details = raw_data.get("accommodation_details") or {}

        label_parts = self.common_service.parse_label(raw_data.get("label", ""))
        country_code = (booker.get("address") or {}).get("country", "").upper()

        total_price = (price.get("total_price") or {}).get("booker_currency")
        currency = currencies.get("booker")

        revenue_usd = None
        if total_price and currency:
            rate = self._get_cached_rate(currency)
            if rate:
                revenue_usd = round(float(total_price) * rate, 2)

        return {
            "transaction_id": accommodations.get("reservation"),
            "conversion_key": raw_data.get("label"),
            "property_id": f"BC-{acc_details.get('accommodation')}" if acc_details.get("accommodation") else None,
            "referral_property_id": label_parts.get("referral_property_id"),
            "status": self.common_service.map_status(raw_data.get("status")),
            "travel_purpose": booker.get("travel_purpose"),
            "country_code": country_code,
            "region": self.common_service.get_region(country_code),
            "currency": currency,
            "check_in_date": raw_data.get("start", "")[:10] or None,
            "check_out_date": raw_data.get("end", "")[:10] or None,
            "site_key": label_parts.get("site_key"),
            "device": label_parts.get("device"),
            "total_price": total_price,
            "revenue_usd": revenue_usd,
        }

    def save_all(self, session, raw_bookings: list) -> dict:
        transformed_records  = [self.transform(raw) for raw in raw_bookings]
        return self.booking_repository.bulk_save(session, transformed_records)
