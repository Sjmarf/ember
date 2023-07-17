from typing import Union, Sequence, Optional
from abc import ABC, abstractmethod


def load_size(value: Union["Size", float]) -> "Size":
    if isinstance(value, (float, int)):
        return AbsoluteSize(value)
    return value


class Size(ABC):
    @abstractmethod
    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        pass


class AbsoluteSize(Size):
    """
    Represents an exact number of pixels. The size returned by the
    get() method is always equal to the 'value' attribute of the object.
    """

    def __init__(self, value: int) -> None:
        self.value: int = value

    def __repr__(self) -> str:
        return f"<AbsoluteSize({self.value}px)>"

    def __add__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self.value + other)

    def __sub__(self, other: int) -> "AbsoluteSize":
        return AbsoluteSize(self.value - other)

    def __mul__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self.value * other))

    def __truediv__(self, other: float) -> "AbsoluteSize":
        return AbsoluteSize(int(self.value / other))

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return (self.value)


class FillSize(Size):
    """
    Represents a size relative to the maximum number of pixels available.
    """

    def __init__(
        self,
        value: int,
        percent: float = 1,
    ):
        self.value: int = value
        self.percentage: float = percent

    def __repr__(self) -> str:
        return f"<FillSize({self.percentage*100}% + {self.value})>"

    def __add__(self, other: int) -> "FillSize":
        return FillSize(self.value + other, self.percentage)

    def __sub__(self, other: int) -> "FillSize":
        return FillSize(self.value - other, self.percentage)

    def __mul__(self, other: float) -> "FillSize":
        return FillSize(self.value, self.percentage * other)

    def __truediv__(self, other: float) -> "FillSize":
        return FillSize(self.value, self.percentage / other)

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return (max_value * self.percentage + self.value)


class FitSize(Size):
    """
    Represents a size relative to the minimum number of pixels available.
    """

    def __init__(
        self,
        value: int,
        percent: float = 1,
    ):
        self.value: int = value
        self.percentage: float = percent

    def __repr__(self) -> str:
        return f"<FitSize({self.percentage*100}% + {self.value})>"

    def __add__(self, other: int) -> "FitSize":
        return FitSize(self.value + other, self.percentage)

    def __sub__(self, other: int) -> "FitSize":
        return FitSize(self.value - other, self.percentage)

    def __mul__(self, other: float) -> "FitSize":
        return FitSize(self.value, self.percentage * other)

    def __truediv__(self, other: float) -> "FitSize":
        return FitSize(self.value, self.percentage / other)

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        return (min_value * self.percentage + self.value)


class InterpolatedSize(Size):
    """
    Used by animations to interpolate between two other Size objects.
    """

    def __init__(self, old_size: "Size", new_size: "Size") -> None:
        self.old_size: "Size" = old_size
        self.new_size: "Size" = new_size
        self.progress: float = 0
        
    def __repr__(self) -> str:
        return f"<InterpolatedSize({self.old_size} -> {self.new_size}: {self.progress*100: .0f}%)>"    

    def get(self, min_value: float = 0, max_value: Optional[float] = None) -> float:
        old_val = self.old_size.get(min_value, max_value)
        new_val = self.new_size.get(min_value, max_value)
        return round(old_val + (new_val - old_val) * self.progress)


FIT = FitSize(0)
FILL = FillSize(0)

SizeType = Union[Size, int]
SequenceSizeType = Union[SizeType, Sequence[SizeType]]
OptionalSequenceSizeType = Union[Optional[SizeType], Sequence[Optional[SizeType]]]
