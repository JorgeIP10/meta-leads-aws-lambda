from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send_emails(self, subject, body, destination_emails):
        pass
