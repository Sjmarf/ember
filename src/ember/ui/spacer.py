import pygame
from typing import Union, Optional, Sequence

from ember.ui.has_geometry import HasGeometry
from ..size import Absolute, SizeType, OptionalSequenceSizeType
from ember.position import PositionType, SequencePositionType


ZERO = Absolute(0)


class Spacer(HasGeometry):
    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        super().__init__(rect, pos, x, y, size, w, h, can_focus=False)

    def __repr__(self) -> str:
        return "<Spacer>"


Spacer.w.default_value = ZERO
Spacer.h.default_value = ZERO
