from typing import Optional
from .size import Size


class RelativeSize(Size):
    """
    Represents a size relative to one of the 'get' parameters.
    """

    def __init__(
        self,
        fraction: float = 1,
        offset: int = 0,
    ):
        self._offset: int = offset
        self._fraction: float = fraction
        super().__init__()

    def __repr__(self) -> str:
        return f"<{type(self).__name__}({self._fraction * 100:.2f}% + {self._offset}px)>"

    def __eq__(self, other):
        if isinstance(other, RelativeSize):
            return self._offset == other._offset and self._fraction == other._fraction
        return False

    def __add__(self, other: int) -> "RelativeSize":
        return type(self)(fraction=self._fraction, offset=self._offset + other)

    def __sub__(self, other: int) -> "RelativeSize":
        return type(self)(fraction=self._fraction, offset=self._offset - other)

    def __mul__(self, other: float) -> "RelativeSize":
        return type(self)(fraction=self._fraction * other, offset=self._offset)

    def __truediv__(self, other: float) -> "RelativeSize":
        return type(self)(fraction=self._fraction / other, offset=self._offset)

    def copy(self) -> "RelativeSize":
        return type(self)(fraction=self.fraction, offset=self._offset)
    
    @property
    def offset(self) -> float:
        return self._offset
    
    @offset.setter
    @Size.triggers_trait_update
    def offset(self, value: float) -> None:
        self._offset = value
        
    @property
    def fraction(self) -> float:
        return self._fraction
    
    @fraction.setter
    @Size.triggers_trait_update
    def fraction(self, value: float) -> None:
        self._fraction = value    