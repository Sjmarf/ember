from .size import Size
from abc import ABC, abstractmethod


class ResizableSize(Size, ABC):
    @abstractmethod
    def _set_value(self, value: int) -> None:
        """
        To be called within Resizable only.
        """
        ...
