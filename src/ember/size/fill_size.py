from typing import Optional
from .size import Size

class FillSize(Size):
    """
    Represents a size relative to the maximum number of pixels available.
    """

    relies_on_min_value = False

    def __init__(
        self,
        value: int,
        percent: float = 1,
    ):
        self.value: int = value
        self.percent: float = percent

    def __repr__(self) -> str:
        return f"<FillSize({self.percent * 100}% + {self.value})>"

    def __eq__(self, other):
        if isinstance(other, FillSize):
            return self.value == other.value and self.percent == other.percent
        return False

    def __add__(self, other: int) -> "FillSize":
        return FillSize(self.value + other, self.percent)

    def __sub__(self, other: int) -> "FillSize":
        return FillSize(self.value - other, self.percent)

    def __mul__(self, other: float) -> "FillSize":
        return FillSize(self.value, self.percent * other)

    def __truediv__(self, other: float) -> "FillSize":
        return FillSize(self.value, self.percent / other)

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return max_value * self.percent + self.value
