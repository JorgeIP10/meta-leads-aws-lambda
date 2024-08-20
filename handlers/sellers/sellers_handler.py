from abc import ABC, abstractmethod


class BasicSellersHandler(ABC):
    @abstractmethod
    def add(self, seller):
        pass

    @abstractmethod
    def get_quantity(self):
        pass

    @abstractmethod
    def update(self, seller_id, new_data):
        pass

    @abstractmethod
    def remove(self):
        pass
