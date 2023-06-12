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
        _ignore_fill: bool = False,
        mode="width",
    ) -> float:
        if self.mode == SizeMode.FILL:
            if _ignore_fill:
                return max_value
            return max_value * self.percentage + self.value
        elif self.mode == SizeMode.FIT:
            if hasattr(element, f"_fit_{mode}"):
                val = (
                    element._fit_width if mode == "width" else element._fit_height
                ) + self.value
            else:
                raise AttributeError(
                    f"Element of type '{type(element).__name__}' cannot have a FIT {mode}."
                )
        else:
            val = self.value

        return val

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


class SizeRange:
    def __init__(
        self,
        minimum: Union[Size, int],
        ideal: Union[Size, int],
        maximum: Union[Size, int],
    ):
        self._min: Size = Size._load(minimum)
        self._ideal: Size = Size._load(ideal)
        self._max: Size = Size._load(maximum)
        self._has_fit_size: bool = False
        self._has_fill_size: bool = False
        self._size_changed()

    def _size_changed(self):
        self._has_fit_size = any(i.mode == SizeMode.FIT for i in (self._min, self._ideal, self._max))
        self._has_fill_size = any(i.mode == SizeMode.FILL for i in (self._min, self._ideal, self._max))
    @property
    def min(self) -> Size:
        return self._min

    @min.setter
    def min(self, value: Union[Size, int]) -> None:
        self._min = Size._load(value)
        self._size_changed()

    @property
    def ideal(self) -> Size:
        return self._ideal

    @ideal.setter
    def ideal(self, value: Union[Size, int]) -> None:
        self._ideal = Size._load(value)
        self._size_changed()

    @property
    def max(self) -> Size:
        return self._max

    @max.setter
    def max(self, value: Union[Size, int]) -> None:
        self._max = Size._load(value)
        self._size_changed()


FIT = Size(0, mode=SizeMode.FIT)
FILL = Size(0, mode=SizeMode.FILL)

FILLRANGE = SizeRange(FIT, FILL, FILL)
FITRANGE = SizeRange(FIT, FIT, FIT)

SizeType = Union[Size, int, SizeRange]
SequenceSizeType = Union[SizeType, Sequence[SizeType]]


def create_range(size: Union[Size, int]) -> SizeRange:
    size: Size = Size._load(size)
    if size is FIT:
        return FITRANGE
    if size is FILL:
        return FILLRANGE
    if size.mode == SizeMode.ABSOLUTE:
        return SizeRange(size.value, size.value, size.value)
    if size.mode == SizeMode.FIT:
        return SizeRange(size, size, size)
    if size.mode == SizeMode.FILL:
        return SizeRange(FIT, size, size)
