from typing import Optional
from .size import Size

class FillSize(Size):
    """
    Represents a size relative to the maximum number of pixels available.
    """

    relies_on_min_value = False

    def __init__(
        self,
        fraction: float = 1,
        offset: int = 0,
    ):
        self.offset: int = offset
        self.fraction: float = fraction

    def __repr__(self) -> str:
        return f"<FillSize({self.fraction * 100}% + {self.offset})>"

    def __eq__(self, other):
        if isinstance(other, FillSize):
            return self.offset == other.offset and self.fraction == other.fraction
        return False

    def __add__(self, other: int) -> "FillSize":
        return FillSize(self.fraction, self.offset + other)

    def __sub__(self, other: int) -> "FillSize":
        return FillSize(self.fraction, self.offset - other)

    def __mul__(self, other: float) -> "FillSize":
        return FillSize(self.fraction * other, self.offset)

    def __truediv__(self, other: float) -> "FillSize":
        return FillSize(self.fraction / other, self.offset)

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0) -> float:
        return max_value * self.fraction + self.offset
