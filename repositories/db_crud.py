from abc import ABC, abstractmethod


class DBCrud(ABC):
    @abstractmethod
    def create(self, rows):
        pass
