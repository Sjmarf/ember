from abc import ABC, abstractmethod

class Position(ABC):
    @abstractmethod
    def get(self, container_size: float = 0, element_size: float = 0) -> float:
        ...
