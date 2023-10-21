from typing import Union as _Union, Sequence as _Sequence, Optional as _Optional
from .position import Position, AbsolutePosition, PivotablePosition, load_position
from .anchor_position import (
    AnchorPosition,
    LeftPosition,
    RightPosition,
    TopPosition,
    BottomPosition,
    CenterPosition,
)
from .interpolated_position import InterpolatedPosition
from .dual_position import (
    DualPosition,
    XDualPosition,
    YDualPosition,
    XYDualPosition,
    TopLeftPosition,
    TopRightPosition,
    BottomLeftPosition,
    BottomRightPosition,
    MidTopPosition,
    MidBottomPosition,
    MidRightPosition,
    MidLeftPosition,
)

PositionType = _Union[int, Position]

SequencePositionType = _Union[PositionType, _Sequence[PositionType], DualPosition]
OptionalSequencePositionType = _Union[
    _Optional[PositionType], _Sequence[_Optional[PositionType]], DualPosition
]
# These exist for type-hinting in Resizable.handles etc

LeftCenterRight = _Union[LeftPosition, CenterPosition, RightPosition]
TopCenterBottom = _Union[TopPosition, CenterPosition, BottomPosition]
BasicPosition = _Union[
    LeftPosition, RightPosition, TopPosition, BottomPosition, CenterPosition
]
CardinalPosition = _Union[
    MidLeftPosition, MidRightPosition, MidTopPosition, MidBottomPosition
]
OrdinalPosition = _Union[
    TopLeftPosition, TopRightPosition, BottomLeftPosition, BottomRightPosition
]
DirectionalPosition = _Union[CardinalPosition, OrdinalPosition, CenterPosition]

LEFT = LeftPosition(0, 0)
RIGHT = RightPosition(0, 1)
TOP = TopPosition(0, 0, 0)
BOTTOM = BottomPosition(0, 1)

TOPLEFT = TopLeftPosition(LEFT, TOP)
TOPRIGHT = TopRightPosition(RIGHT, TOP)
BOTTOMLEFT = BottomLeftPosition(LEFT, BOTTOM)
BOTTOMRIGHT = BottomRightPosition(RIGHT, BOTTOM)
CENTER = CenterPosition(0, 0.5)
MIDLEFT = MidLeftPosition(LEFT, CENTER)
MIDRIGHT = MidRightPosition(RIGHT, CENTER)
MIDTOP = MidTopPosition(CENTER, TOP)
MIDBOTTOM = MidBottomPosition(CENTER, BOTTOM)
