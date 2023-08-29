from typing import Optional
from .size import Size

from .. import log


class RatioSize(Size):
    relies_on_other_value = True

    def __init__(
        self,
        value: int = 0,
        percent: float = 1,
    ):
        self.value: int = value
        self.percent: float = percent

    def __add__(self, other: int) -> "RatioSize":
        return RatioSize(self.value + other, self.percent)

    def __sub__(self, other: int) -> "RatioSize":
        return RatioSize(self.value - other, self.percent)

    def __mul__(self, other: float) -> "RatioSize":
        return RatioSize(self.value, self.percent * other)

    def __truediv__(self, other: float) -> "RatioSize":
        return RatioSize(self.value, self.percent / other)

    def get(self, min_value: float = 0, max_value: Optional[float] = None, other_value: float = 0) -> float:
        return other_value * self.percent + self.value
