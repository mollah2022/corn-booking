from abc import ABC, abstractmethod


class BookingRepositoryInterface(ABC):

    @abstractmethod
    def find_by_transaction_id(self, transaction_id: str):
        pass

    @abstractmethod
    def insert(self, booking_data: dict):
        pass

    @abstractmethod
    def update(self, booking, booking_data: dict):
        pass

    @abstractmethod
    def bulk_save(self,records: list) -> dict:
        pass