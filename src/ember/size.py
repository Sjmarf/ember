from typing import Union, Sequence, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class Size:
    def __init__(
        self,
        value: int,
        percent: float = 1,
        mode: Union[int, Literal["absolute", "fit", "fill"]] = 0,
    ):
        self.value: int = value
        self.percentage: float = percent

        if type(mode) is str:
            if mode in ["absolute", "fit", "fill"]:
                mode = ["absolute", "fit", "fill"].index(mode)
            else:
                raise ValueError(
                    f"Mode must be an int or one of 'absolute', 'fit' or 'fill' - not '{mode}'."
                )
        elif type(mode) is int:
            if not (0 <= mode <= 2):
                raise ValueError(f"Mode must be between 0 and 2 inclusive, not {mode}.")
        else:
            raise ValueError(f"Mode must be an int or str, not {type(mode).__name__}.")

        # Modes:
        # 0: absolute, 1: fit, 2: fill
        self.mode = mode

    def get(
        self,
        element: "Element",
        max_value: Optional[float] = None,
        _ignore_fill: bool = False,
        mode="width",
    ) -> float:
        if self.mode == 2:
            if _ignore_fill:
                return max_value
            return max_value * self.percentage + self.value
        elif self.mode == 1:

            if hasattr(element, f"_fit_{mode}"):
                val = (element._fit_width if mode == "width" else element._fit_height) + self.value
            else:
                raise AttributeError(
                    f"Element of type '{type(element).__name__}' cannot have a FIT {mode}."
                )
        else:
            val = self.value

        return val

    def __repr__(self):
        if self.mode == 0:
            return f"<Size({self.value}px)>"
        else:
            message = "<Size("
            if self.percentage != 1:
                message += "" f"{self.percentage * 100}% of "

            message += "FIT" if self.mode == 1 else "FILL"

            if self.value != 0:
                message += f" {self.value}px"

            return f"{message})>"

    def __add__(self, other):
        if type(other) in {int, float}:
            return Size(self.value + other, self.percentage, mode=self.mode)

        elif type(other) is Size:
            if self.mode == 0:
                mode = other.mode
            else:
                mode = self.mode

            return Size(self.value + other.value, self.percentage, mode=mode)

        else:
            return NotImplemented

    def __sub__(self, other):
        if type(other) in {int, float}:
            return Size(self.value - other, self.percentage, mode=self.mode)

        elif type(other) is Size:
            if self.mode == 0:
                mode = other.mode
            else:
                mode = self.mode

            return Size(self.value + other.value, self.percentage, mode=mode)

        else:
            return NotImplemented

    def __mul__(self, other):
        if type(other) in {int, float}:
            if self.mode == 0:
                return Size(self.value * other, self.percentage, mode=self.mode)
            return Size(self.value, self.percentage * other, mode=self.mode)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if type(other) in {int, float}:
            if self.mode == 0:
                return Size(self.value / other, self.percentage, mode=self.mode)
            return Size(self.value, self.percentage / other, mode=self.mode)
        else:
            return NotImplemented


FIT = Size(0, mode=1)
FILL = Size(0, mode=2)

SizeType = Union[Size, int, None]
SequenceSizeType = Union[SizeType, Sequence[SizeType], None]
