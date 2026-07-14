from abc import ABC, abstractmethod


class BookingApiInterface(ABC):

    @abstractmethod
    def fetch_bookings(self, updated_from: str, updated_to: str) -> list:
        pass