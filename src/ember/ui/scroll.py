from typing import Iterable, Optional, Union, Sequence
import itertools

import pygame

from .element import Element
from .masked_container import MaskedContainer
from .box import Box
from .can_pivot import CanPivot
from ..common import ElementType
from ..position import PositionType, SequencePositionType, PivotablePosition
from ..size import OptionalSequenceSizeType, SizeType
from ..trait.cascading_trait_value import CascadingTraitValue


class Scroll(MaskedContainer, Box, CanPivot):
    def __init__(
        self,
        element: Optional[ElementType] = None,
        cascading: Union[CascadingTraitValue, Sequence[CascadingTraitValue]] = (),
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        super().__init__(
            element=element,
            cascading=cascading,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
        )

        position = PivotablePosition(0, 0, watching=self)
        self.cascading.add(Element.x(position))
        self.cascading.add(Element.y(~position))
