from abc import ABC, abstractmethod


class PrioritySellersHandler(ABC):
    @abstractmethod
    def add(self, seller, priority: int):
        pass

    @abstractmethod
    def get_quantity(self):
        pass

    @abstractmethod
    def update(self, seller_id, new_data, priority: int = None):
        pass

    @abstractmethod
    def remove(self):
        pass
