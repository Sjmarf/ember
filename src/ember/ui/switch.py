from typing import Optional, Union, Sequence
from abc import ABC, abstractmethod
import pygame
import itertools

from ember.axis import Axis, HORIZONTAL

from .toggle_button import ToggleButton
from .two_panel_container import TwoPanelContainer
from ..material import Material

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
from .panel import Panel
from ..common import SequenceElementType

from ..on_event import on_event


class Switch(TwoPanelContainer, ToggleButton, ABC):
    animation: Animation = EaseInOut(0.2)

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
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
            *elements,
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
            **kwargs
        )
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

        x = RIGHT if self.active else LEFT
        y = TOP if self.active else BOTTOM
        self.cascading.add(Element.x(PivotablePosition(x, 0, watching=self)))
        self.cascading.add(Element.y(PivotablePosition(0, y, watching=self)))

        self.cascading.add(Element.w(PivotableSize(RATIO, FILL, watching=self)))
        self.cascading.add(Element.h(PivotableSize(FILL, RATIO, watching=self)))
        
    def __repr__(self) -> str:
        return "<Switch>"

    @on_event()
    def _update_panel_material(self) -> None:
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

    @abstractmethod
    def _get_front_material(self) -> "Material":
        ...

    @abstractmethod
    def _get_back_material(self) -> "Material":
        ...

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
            
