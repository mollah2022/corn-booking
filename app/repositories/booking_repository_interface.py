from abc import ABC, abstractmethod


class BookingRepositoryInterface(ABC):

    @abstractmethod
    def find_by_transaction_id(self, session, transaction_id: str):
        pass

    @abstractmethod
    def bulk_save(self, session, records: list) -> dict:
        pass
