from typing import Union, Sequence, Literal, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class SizeMode(Enum):
    ABSOLUTE = 0
    FIT = 1
    FILL = 2


class Size:
    def __init__(
        self,
        value: int,
        percent: float = 1,
        mode: Union[SizeMode, "Size"] = SizeMode.ABSOLUTE,
    ):
        self.value: int = value
        self.percentage: float = percent

        if isinstance(mode, Size):
            mode = mode.mode
        else:
            mode = mode

        # Modes:
        self.mode: SizeMode = mode

    @classmethod
    def _load(cls, size) -> "Size":
        return cls(size) if isinstance(size, (int, float)) else size

    def get(
        self,
        element: "Element",
        max_value: Optional[float] = None,
        mode="width",
    ) -> float:
        if self.mode == SizeMode.FILL:
            return max_value * self.percentage + self.value
        elif self.mode == SizeMode.FIT:
            return (
                element._min_w if mode == "width" else element._min_h
            ) + self.value
        else:
            return self.value

    def __repr__(self) -> str:
        if self.mode == SizeMode.ABSOLUTE:
            return f"<Size({self.value}px)>"
        else:
            message = "<Size("
            if self.percentage != 1:
                message += "" f"{self.percentage * 100}% of "

            message += "FIT" if self.mode == SizeMode.FIT else "FILL"

            if self.value != 0:
                message += f" {self.value}px"

            return f"{message})>"

    def __add__(self, other: Union[int, float, "Size"]):
        if isinstance(other, (int, float)):
            return Size(self.value + other, self.percentage, mode=self.mode)

        elif isinstance(other, Size):
            if self.mode == SizeMode.ABSOLUTE:
                mode = other.mode
            else:
                mode = self.mode

            return Size(self.value + other.value, self.percentage, mode=mode)

        else:
            return NotImplemented

    def __sub__(self, other: Union[int, float, "Size"]):
        if isinstance(other, (int, float)):
            return Size(self.value - other, self.percentage, mode=self.mode)

        elif isinstance(other, Size):
            if self.mode == SizeMode.ABSOLUTE:
                mode = other.mode
            else:
                mode = self.mode

            return Size(self.value + other.value, self.percentage, mode=mode)

        else:
            return NotImplemented

    def __mul__(self, other: Union[int, float]):
        if isinstance(other, (int, float)):
            if self.mode == SizeMode.ABSOLUTE:
                return Size(self.value * other, self.percentage, mode=self.mode)
            return Size(self.value, self.percentage * other, mode=self.mode)
        else:
            return NotImplemented

    def __truediv__(self, other: Union[int, float]):
        if isinstance(other, (int, float)):
            if self.mode == SizeMode.ABSOLUTE:
                return Size(self.value / other, self.percentage, mode=self.mode)
            return Size(self.value, self.percentage / other, mode=self.mode)
        else:
            return NotImplemented


FIT = Size(0, mode=SizeMode.FIT)
FILL = Size(0, mode=SizeMode.FILL)

SizeType = Union[Size, int]
SequenceSizeType = Union[SizeType, Sequence[SizeType]]
