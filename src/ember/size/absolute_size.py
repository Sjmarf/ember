from .resizable_size import ResizableSize
from typing import Optional


class AbsoluteSize(ResizableSize):
    """
    Represents an exact number of pixels. The size returned by the
    get() method is always equal to the 'value' attribute of the object.
    """

    relies_on_min_value = False

    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"<AbsoluteSize({self.value}px)>"

    def __eq__(self, other):
        if isinstance(other, AbsoluteSize):
            return self.value == other.value
        return False

    def __add__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self.value + other)

    def __sub__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self.value - other)

    def __mul__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self.value * other))

    def __truediv__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self.value / other))

    def _set_value(self, value: int) -> None:
        self.value = value

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0) -> float:
        return self.value
