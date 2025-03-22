from abc import ABC, abstractmethod


class Service(ABC):
    service_item: str

    @abstractmethod
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def preference_layout(self, layout):
        pass