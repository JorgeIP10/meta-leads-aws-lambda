from abc import ABC, abstractmethod


class TemplateRenderer(ABC):
    @abstractmethod
    def render(self, context):
        pass
