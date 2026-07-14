import requests
from app.api_client.booking_api_interface import BookingApiInterface


class BookingApiClient(BookingApiInterface):

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key

    def fetch_bookings(self, updated_from: str, updated_to: str) -> list:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        params = {
            "updated_from": updated_from,
            "updated_to": updated_to,
        }

        response = requests.get(
            f"{self.base_url}/bookings",
            headers=headers,
            params=params,
            timeout=15,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])