from typing import Union, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class Position:
    def __init__(self, value: int, percent: float = 1, size_offset: float = 0):
        self.value: int = value
        self.percent: float = percent
        self.size_offset: float = size_offset

    def get(
        self, element: "Element", max_value: float = 0, element_size: float = 0, _ignore_fill: bool = False
    ) -> float:
        return round(max_value * self.percent) + round(element_size * self.size_offset) + self.value

    def __repr__(self):
        return f"<Position({self.value})>"

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Position(self.value + other, self.percent, self.size_offset)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Position(self.value - other, self.percent, self.size_offset)
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Position(self.value, self.percent * other)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Position(self.value, self.percent / other)
        else:
            return NotImplemented


PositionType = Union[
    Sequence[int],
    Position,
    Sequence[Position],
    None,
]

LEFT = Position(0, 0, 0)
RIGHT = Position(0, 1, -1)
TOP = LEFT
BOTTOM = RIGHT

TOPLEFT = (LEFT, TOP)
TOPRIGHT = (RIGHT, TOP)
BOTTOMLEFT = (LEFT, BOTTOM)
BOTTOMRIGHT = (BOTTOM, RIGHT)
CENTER = Position(0, 0.5, -0.5)
MIDLEFT = (LEFT, CENTER)
MIDRIGHT = (RIGHT, CENTER)
MIDTOP = (CENTER, TOP)
MIDBOTTOM = (CENTER, BOTTOM)


