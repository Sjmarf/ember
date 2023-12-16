from .size import Size
from typing import Optional

from ember.axis import Axis, VERTICAL

class Absolute(Size):
    """
    Represents an exact number of pixels. The size returned by the
    get() method is always equal to the 'value' attribute of the object.
    """

    relies_on_min_value = False

    def __init__(self, value: int) -> None:
        self._value: int = value
        super().__init__()

    def __repr__(self) -> str:
        return f"<AbsoluteSize({self._value}px)>"

    def __eq__(self, other):
        if isinstance(other, Absolute):
            return self._value == other._value
        elif isinstance(other, (float, int)):
            return self._value == other
        return False
    
    def __hash__(self) -> int:
        return hash(self._value)

    def __add__(self, other: int) -> "Absolute":
        return Absolute(self._value + other)

    def __sub__(self, other: int) -> "Absolute":
        return Absolute(self._value - other)

    def __mul__(self, other: float) -> "Absolute":
        return Absolute(int(self._value * other))

    def __truediv__(self, other: float) -> "Absolute":
        return Absolute(int(self._value / other))

    def _get(self) -> float:
        return self._value
    
    def copy(self) -> "Absolute":
        return Absolute(self._value)

    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    @Size.triggers_trait_update
    def value(self, value: int) -> None:
        self._value = value
