from typing import Optional, Union, Sequence
from abc import ABC, abstractmethod
import pygame

from ember.axis import Axis, HORIZONTAL

from .toggle_button import ToggleButton
from .handled_element import UpdatingHandleElement
from ..material import Material
from ember.ui.panel import Panel

from ..event import TOGGLEDON, TOGGLEDOFF

from ..size import SizeType, OptionalSequenceSizeType, FILL, RATIO, PivotableSize
from ember.position import (
    PositionType,
    SequencePositionType,
    PivotablePosition,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
)

from ember.animation import Animation, EaseInOut

from ember.ui.element import Element
from ..common import ElementType

from ..on_event import on_event


class Switch(UpdatingHandleElement, ToggleButton, ABC):
    animation: Animation = EaseInOut(0.2)

    def __init__(
        self,
        element: Optional[ElementType] = None,
        active: bool = False,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        axis: Axis = HORIZONTAL,
        **kwargs
    ):
        super().__init__(
            element,
            active=active,
            disabled=disabled,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            axis=axis,
            back_panel=Panel(None, y=0, size=FILL),
            **kwargs
        )
        x = RIGHT if self.active else LEFT
        y = TOP if self.active else BOTTOM
        self.cascading.add(Element.x(PivotablePosition(x, 0, watching=self)))
        self.cascading.add(Element.y(PivotablePosition(0, y, watching=self)))

        self.cascading.add(Element.w(PivotableSize(RATIO, FILL, watching=self)))
        self.cascading.add(Element.h(PivotableSize(FILL, RATIO, watching=self)))
        
    def __repr__(self) -> str:
        return "<Switch>"

    @on_event(TOGGLEDON)
    def _move_handle_active(self):
        with self.animation:
            self.cascading.add(Element.x(PivotablePosition(RIGHT, 0, watching=self)))
            self.cascading.add(Element.y(PivotablePosition(0, TOP, watching=self)))

    @on_event(TOGGLEDOFF)
    def _move_handle_inactive(self):
        with self.animation:
            self.cascading.add(Element.x(PivotablePosition(LEFT, 0, watching=self)))
            self.cascading.add(Element.y(PivotablePosition(0, BOTTOM, watching=self)))
            
