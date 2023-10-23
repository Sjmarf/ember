from .size import Size
from .resizable_size import ResizableSize
from typing import Optional

from ember_ui.axis import Axis, VERTICAL

class AbsoluteSize(ResizableSize):
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
        if isinstance(other, AbsoluteSize):
            return self._value == other._value
        elif isinstance(other, (float, int)):
            return self._value == other
        return False

    def __add__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self._value + other)

    def __sub__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self._value - other)

    def __mul__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self._value * other))

    def __truediv__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self._value / other))

    def _set_value(self, value: int) -> None:
        self._value = value

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0, axis: Axis = VERTICAL) -> float:
        return self._value
    
    def copy(self) -> "AbsoluteSize":
        return AbsoluteSize(self._value)

    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    @Size.triggers_trait_update
    def value(self, value: int) -> None:
        self._value = value