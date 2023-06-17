from typing import Union, Sequence, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class Position:
    __slots__ = ("value", "percent", "size_offset")

    def __init__(self, value: int, percent: float = 0, size_offset: float = 0):
        self.value: int = value
        self.percent: float = percent
        self.size_offset: float = size_offset
    
    @classmethod
    def _load(cls, pos) -> "Position":
        return cls(pos) if isinstance(pos, (int, float)) else pos    

    def get(
        self,
        element: Optional["Element"],
        max_value: float = 0,
        element_size: float = 0,
        _ignore_fill: bool = False,
    ) -> float:
        return (
            round(max_value * self.percent)
            + round(element_size * self.size_offset)
            + self.value
        )

    def __repr__(self):
        return f"<Position({self.value})>"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value + other, self.percent, self.size_offset)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value - other, self.percent, self.size_offset)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value, self.percent * other)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return type(self)(self.value, self.percent / other)
        else:
            return NotImplemented


PositionType = Union[int, Position]

SequencePositionType = Union[PositionType, Sequence[PositionType]]


# These exist for type-hinting in Text.align etc


class LeftPosition(Position):
    pass


class RightPosition(Position):
    pass


class TopPosition(Position):
    pass


class BottomPosition(Position):
    pass


class CenterPosition(Position):
    pass


LeftCenterRight = Union[LeftPosition, CenterPosition, RightPosition]
TopCenterBottom = Union[TopPosition, CenterPosition, BottomPosition]
CardinalPosition = Union[
    LeftPosition, RightPosition, TopPosition, BottomPosition, CenterPosition
]

LEFT = LeftPosition(0, 0, 0)
RIGHT = RightPosition(0, 1, -1)
TOP = TopPosition(0, 0, 0)
BOTTOM = BottomPosition(0, 1, -1)

TOPLEFT = (LEFT, TOP)
TOPRIGHT = (RIGHT, TOP)
BOTTOMLEFT = (LEFT, BOTTOM)
BOTTOMRIGHT = (BOTTOM, RIGHT)
CENTER = CenterPosition(0, 0.5, -0.5)
MIDLEFT = (LEFT, CENTER)
MIDRIGHT = (RIGHT, CENTER)
MIDTOP = (CENTER, TOP)
MIDBOTTOM = (CENTER, BOTTOM)
