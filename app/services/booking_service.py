from app.services.common_service import CommonService


class BookingService:

    def __init__(self, booking_repository):
        self.booking_repository = booking_repository
        self._rate_cache = {}

    def _get_cached_rate(self, currency: str) -> float:
        if currency not in self._rate_cache:
            self._rate_cache[currency] = CommonService.get_exchange_rate(currency, "USD")
        return self._rate_cache[currency]

    def transform(self, raw_data: dict) -> dict:
        accommodations = raw_data.get("accommodations") or {}
        booker = raw_data.get("booker") or {}
        currencies = raw_data.get("currencies") or {}
        price = raw_data.get("price") or {}
        acc_details = raw_data.get("accommodation_details") or {}

        label_parts = CommonService.parse_label(raw_data.get("label", ""))
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
            "status": CommonService.map_status(raw_data.get("status")),
            "travel_purpose": booker.get("travel_purpose"),
            "country_code": country_code,
            "region": CommonService.get_region(country_code),
            "currency": currency,
            "check_in_date": raw_data.get("start", "")[:10] or None,
            "check_out_date": raw_data.get("end", "")[:10] or None,
            "site_key": label_parts.get("site_key"),
            "device": label_parts.get("device"),
            "total_price": total_price,
            "revenue_usd": revenue_usd,
        }

    def save(self, raw_data: dict) -> str:
        transformed = self.transform(raw_data)
        existing = self.booking_repository.find_by_transaction_id(transformed["transaction_id"])

        if existing:
            self.booking_repository.update(existing, transformed)
            return "updated"
        else:
            self.booking_repository.insert(transformed)
            return "inserted"
