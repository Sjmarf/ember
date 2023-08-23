import pygame
from typing import Union, Optional, Sequence, TYPE_CHECKING

from .. import common as _c
from ..common import SequenceElementType, DEFAULT

from ember.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType, TOP
)
from ..size import SizeType, OptionalSequenceSizeType

from .base.mixin.style import StyleType

if TYPE_CHECKING:
    from ember.style.style import Style
    from .base.element import Element


from .base.scroll import Scroll
from .base.mixin.content_size_direction import VerticalContentSize
from .base.mixin.content_pos_direction import VerticalContentPos


class VScroll(VerticalContentPos, VerticalContentSize, Scroll):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional[StyleType] = DEFAULT,
    ):
        super().__init__(
            # MultiElementContainer
            *elements,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            style=style,
            # ContentPos
            content_pos=content_pos,
            content_x=content_x,
            content_y=content_y,
            # ContentSize
            content_size=content_size,
            content_w=content_w,
            content_h=content_h,
        )

        self._content_y.default_value = TOP

    def __repr__(self) -> str:
        return "<VScroll>"

    def make_visible(self, element: "Element") -> None:
        container = self._elements[self.scrollable_element_index]
        if container not in element.ancestry:
            return self.parent.make_visible(element)

        if element.rect.top > self.rect.bottom:
            self.set_scroll(
                element.rect.bottom - container.rect.top - self.rect.h,
                cause=Scroll.MovementCause.VISIBILITY,
            )
        else:
            self.set_scroll(
                element.rect.top - container.rect.top,
                cause=Scroll.MovementCause.VISIBILITY,
            )
