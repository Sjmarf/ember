from typing import Optional
from .size import Size


class FitSize(Size):
    """
    Represents a size relative to the minimum number of pixels available.
    """

    relies_on_min_value = True

    def __init__(
        self,
        fraction: float = 1,
        offset: int = 0,
    ):
        self.offset: int = offset
        self.fraction: float = fraction

    def __repr__(self) -> str:
        return f"<FitSize({self.fraction * 100}% + {self.offset})>"

    def __eq__(self, other):
        if isinstance(other, FitSize):
            return self.offset == other.offset and self.fraction == other.fraction
        return False

    def __add__(self, other: int) -> "FitSize":
        return FitSize(self.fraction, self.offset + other)

    def __sub__(self, other: int) -> "FitSize":
        return FitSize(self.fraction, self.offset - other)

    def __mul__(self, other: float) -> "FitSize":
        return FitSize(self.fraction * other, self.offset)

    def __truediv__(self, other: float) -> "FitSize":
        return FitSize(self.fraction / other, self.offset)

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0) -> float:
        return min_value * self.fraction + self.offset
