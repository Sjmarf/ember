import pygame
from ..common import SequenceElementType, FocusType
from typing import Optional, Union, Sequence

from ember.base.stack import Stack
from ember.size import SizeType, OptionalSequenceSizeType
from ember.position import (
    PositionType,
    SequencePositionType,
)
from ..spacing import SpacingType

from ember.trait.cascading_trait_value import CascadingTraitValue

class VStack(Stack):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        cascading: Union[CascadingTraitValue, Sequence[CascadingTraitValue]] = (),
        spacing: Optional[SpacingType] = None,
        focus_on_entry: Optional[FocusType] = None,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
    ):
        super().__init__(
            # Stack
            *elements,
            spacing=spacing,
            focus_on_entry=focus_on_entry,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            cascading=cascading
        )

    def __repr__(self) -> str:
        return f"<VStack({len(self._elements)} elements)>"
