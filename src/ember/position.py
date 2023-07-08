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
    def _load(cls, pos: Union["Position", int, float, None]) -> Optional["Position"]:
        return cls(pos) if isinstance(pos, (int, float)) else pos

    def get(self, container_size: float = 0, element_size: float = 0) -> float:
        return (
            (container_size * self.percent)
            + (element_size * self.size_offset)
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


class DualPosition:
    def __init__(self, x: Position, y: Position):
        self.x = x
        self.y = y


class XYDualPosition(DualPosition):
    def __add__(self, other):
        self.x += other
        self.y += other
        return self

    def __sub__(self, other):
        self.x -= other
        self.y -= other
        return self

    def __mul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __truediv__(self, other):
        self.x /= other
        self.y /= other
        return self


class XDualPosition(DualPosition):
    def __add__(self, other):
        self.x += other
        return self

    def __sub__(self, other):
        self.x -= other
        return self

    def __mul__(self, other):
        self.x *= other
        return self

    def __truediv__(self, other):
        self.x /= other
        return self


class YDualPosition(DualPosition):
    def __add__(self, other):
        self.y += other
        return self

    def __sub__(self, other):
        self.y -= other
        return self

    def __mul__(self, other):
        self.y *= other
        return self

    def __truediv__(self, other):
        self.y /= other
        return self


PositionType = Union[int, Position]

SequencePositionType = Union[PositionType, Sequence[PositionType], DualPosition]
OptionalSequencePositionType = Union[
    Optional[PositionType], Sequence[Optional[PositionType]], DualPosition
]

# These exist for type-hinting in Resizable.handles etc


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


class TopLeftPosition(XYDualPosition):
    pass


class TopRightPosition(XYDualPosition):
    pass


class BottomLeftPosition(XYDualPosition):
    pass


class BottomRightPosition(XYDualPosition):
    pass


class MidLeftPosition(XDualPosition):
    pass


class MidRightPosition(XDualPosition):
    pass


class MidTopPosition(YDualPosition):
    pass


class MidBottomPosition(YDualPosition):
    pass


LeftCenterRight = Union[LeftPosition, CenterPosition, RightPosition]
TopCenterBottom = Union[TopPosition, CenterPosition, BottomPosition]
BasicPosition = Union[
    LeftPosition, RightPosition, TopPosition, BottomPosition, CenterPosition
]
CardinalPosition = Union[MidLeftPosition, MidRightPosition, MidTopPosition, MidBottomPosition]
OrdinalPosition = Union[TopLeftPosition, TopRightPosition, BottomLeftPosition, BottomRightPosition]
DirectionalPosition = Union[CardinalPosition, OrdinalPosition, CenterPosition]

LEFT = LeftPosition(0, 0, 0)
RIGHT = RightPosition(0, 1, -1)
TOP = TopPosition(0, 0, 0)
BOTTOM = BottomPosition(0, 1, -1)

TOPLEFT = TopLeftPosition(TOP, LEFT)
TOPRIGHT = TopRightPosition(TOP, RIGHT)
BOTTOMLEFT = BottomLeftPosition(LEFT, BOTTOM)
BOTTOMRIGHT = BottomRightPosition(RIGHT, BOTTOM)
CENTER = CenterPosition(0, 0.5, -0.5)
MIDLEFT = MidLeftPosition(LEFT, CENTER)
MIDRIGHT = MidRightPosition(RIGHT, CENTER)
MIDTOP = MidTopPosition(CENTER, TOP)
MIDBOTTOM = MidBottomPosition(CENTER, BOTTOM)
