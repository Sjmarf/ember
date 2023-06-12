import pygame
from typing import Union, Optional, Sequence

from .base.element import Element
from ..size import Size, FILL, SizeType, SequenceSizeType
from ..position import PositionType, SequencePositionType


class Spacer(Element):
    def __init__(
        self,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        width: Optional[SizeType] = None,
        height: Optional[SizeType] = None,
    ):

        super().__init__(rect, pos, x, y, size, width, height, can_focus=False, default_size=(0,0))

    def __repr__(self) -> str:
        return "<Spacer>"
