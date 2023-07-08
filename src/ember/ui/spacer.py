import pygame
from typing import Union, Optional, Sequence

from .base.element import Element
from ..size import Size, FILL, SizeType, OptionalSequenceSizeType
from ..position import PositionType, SequencePositionType


class Spacer(Element):
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

        super().__init__(rect, pos, x, y, size, w, h, default_size=(Size(0), Size(0)), can_focus=False)

    def __repr__(self) -> str:
        return "<Spacer>"
