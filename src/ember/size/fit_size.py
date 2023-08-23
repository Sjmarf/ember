from typing import Optional
from .size import Size


class FitSize(Size):
    """
    Represents a size relative to the minimum number of pixels available.
    """

    relies_on_min_value = True

    def __init__(
        self,
        value: int,
        percent: float = 1,
    ):
        self.value: int = value
        self.percent: float = percent

    def __repr__(self) -> str:
        return f"<FitSize({self.percent * 100}% + {self.value})>"

    def __eq__(self, other):
        if isinstance(other, FitSize):
            return self.value == other.value and self.percent == other.percent
        return False

    def __add__(self, other: int) -> "FitSize":
        return FitSize(self.value + other, self.percent)

    def __sub__(self, other: int) -> "FitSize":
        return FitSize(self.value - other, self.percent)

    def __mul__(self, other: float) -> "FitSize":
        return FitSize(self.value, self.percent * other)

    def __truediv__(self, other: float) -> "FitSize":
        return FitSize(self.value, self.percent / other)

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return min_value * self.percent + self.value
