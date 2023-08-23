from typing import Optional
from .size import Size


class RatioSize(Size):
    def __init__(
        self,
        value: int = 0,
        percent: float = 1,
    ):
        self.value: int = value
        self.percent: float = percent
        self.pair_value: float = 0

    def __add__(self, other: int) -> "RatioSize":
        return RatioSize(self.value + other, self.percent)

    def __sub__(self, other: int) -> "RatioSize":
        return RatioSize(self.value - other, self.percent)

    def __mul__(self, other: float) -> "RatioSize":
        return RatioSize(self.value, self.percent * other)

    def __truediv__(self, other: float) -> "RatioSize":
        return RatioSize(self.value, self.percent / other)

    def update_pair_value(self, value: float) -> bool:
        if self.pair_value != value:
            self.pair_value = value
            return True
        return False

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return self.pair_value * self.percent + self.value
