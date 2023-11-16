import pygame
from abc import ABC
from typing import Optional, Union, Sequence
from .gauge import Gauge
from ember import log
from ember.ui.single_element_container import SingleElementContainer
from ember.ui.panel import Panel
from .can_pivot import CanPivot

from ember.ui.element import Element
from .handled_element import UpdatingHandleElement

from ..event import VALUEMODIFIED

from ..size import FILL, PivotableSize, OptionalSequenceSizeType, SizeType
from ember.position import (
    LEFT,
    BOTTOM,
    PivotablePosition,
    PositionType,
    SequencePositionType,
)

from ember.on_event import on_event
from ember.axis import Axis, HORIZONTAL


class Bar(UpdatingHandleElement, Gauge, SingleElementContainer, CanPivot, ABC):
    def __init__(
        self,
        *args,
        value: Optional[float] = 0,
        min_value: float = 0,
        max_value: float = 1,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        axis: Axis = HORIZONTAL,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            value=value,
            min_value=min_value,
            max_value=max_value,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            back_panel=Panel(None, y=0, size=FILL),
            axis=axis,
            **kwargs,
        )

        self.cascading.add(Element.x(PivotablePosition(LEFT, 0, watching=self)))
        self.cascading.add(Element.y(PivotablePosition(0, BOTTOM, watching=self)))

        size = PivotableSize(FILL * self._progress, FILL, watching=self)
        self.cascading.add(Element.w(size))
        self.cascading.add(Element.h(~size))

    @on_event(VALUEMODIFIED)
    def _update_panel_sizes(self):
        with log.size.indent("Updating bar cascading sizes..."):
            size = PivotableSize(FILL * self._progress, FILL, watching=self)
            self.cascading.add(Element.w(size))
            self.cascading.add(Element.h(~size))
