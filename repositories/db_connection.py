from abc import ABC, abstractmethod


class DBConnection(ABC):
    @abstractmethod
    def start_connection(self):
        pass

    @abstractmethod
    def create_cursor(self):
        pass

    @abstractmethod
    def create_connection_cursor(self):
        pass
