import requests
from ratelimit import limits, sleep_and_retry
from app.data.country_region_map import COUNTRY_REGION_MAP
from app.data.status_map import STATUS_MAP

ONE_SECOND = 1
MAX_CALLS_PER_SECOND = 1


class CommonService:

    @staticmethod
    def get_region(country_code: str) -> str:
        if not country_code:
            return None
        return COUNTRY_REGION_MAP.get(country_code.upper(), "other")

    @staticmethod
    def map_status(raw_status: str) -> str:
        return STATUS_MAP.get(raw_status, raw_status)

    @staticmethod
    @sleep_and_retry
    @limits(calls=MAX_CALLS_PER_SECOND, period=ONE_SECOND)
    def get_exchange_rate(base_currency: str, target_currency: str = "USD") -> float:
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["rates"].get(target_currency)

    @staticmethod
    def parse_label(label: str) -> dict:
        parts = label.split("_")
        parsed = {}
        for part in parts:
            if part.startswith("k-"):
                parsed["site_key"] = part[2:].upper()
            elif part.startswith("d-"):
                device_map = {"m": "mobile", "d": "desktop", "t": "tablet"}
                parsed["device"] = device_map.get(part[2:], part[2:])
            elif part.startswith("p-"):
                parsed["referral_property_id"] = part[2:]
        return parsed

    @staticmethod
    def chunk_list(records: list, chunk_size: int):
        """Reusable chunking utility - yields successive chunk_size-sized pieces."""
        for i in range(0, len(records), chunk_size):
            yield records[i:i + chunk_size]
