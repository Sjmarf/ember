import itertools
from typing import Iterable, Optional, Union, Sequence

import pygame

from .element import Element
from .masked_container import MaskedContainer
from .box import Box
from .can_pivot import CanPivot
from ..animation import EaseOut
from ..event import VALUEMODIFIED
from ..axis import Axis, VERTICAL
from ..common import ElementType
from ..position import PositionType, SequencePositionType, PivotablePosition, RIGHT
from ..size import OptionalSequenceSizeType, SizeType
from ..trait.cascading_trait_value import CascadingTraitValue
from .scrollbar import ScrollBar
from ember.trait import Trait

from ember import log

class Scroll(MaskedContainer, Box, CanPivot):
    scrollbar_class: type[ScrollBar] = NotImplemented

    def __init__(
        self,
        element: Optional[ElementType] = None,
        scroll_value: float = 0,
        cascading: Union[CascadingTraitValue, Sequence[CascadingTraitValue]] = (),
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        axis: Axis | None = None,
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
            axis=axis,
        )

        with self.adding_element(
            self.scrollbar_class(x=RIGHT, y=0), update=False
        ) as scrollbar:
            self._scrollbar: ScrollBar = scrollbar

        self._scrollbar_added(scrollbar=scrollbar)

        self._scroll_value: float = -1
        self._max_scroll_value: float = 0

        self.scroll_value = scroll_value

    def __repr__(self) -> str:
        return f"<Scroll>"

    @property
    def scrollbar(self) -> ScrollBar:
        return self._scrollbar

    def _scrollbar_added(self, scrollbar: ScrollBar) -> None:
        with Trait.inspecting(Trait.Layer.PARENT):
            scrollbar.axis = self.axis

    def update_rect(
        self,
        surface: pygame.Surface,
        x: Optional[float] = None,
        y: Optional[float] = None,
        w: Optional[float] = None,
        h: Optional[float] = None,
        rel_pos1: Optional[float] = None,
        rel_pos2: Optional[float] = None,
        rel_size1: Optional[float] = None,
        rel_size2: Optional[float] = None,
    ) -> None:
        super().update_rect(
            surface, x, y, w, h, rel_pos1, rel_pos2, rel_size1, rel_size2
        )
        self._max_scroll_value = self.element.rect.h - self.rect.h
        self._scrollbar.max_value = self._max_scroll_value
        self._scrollbar.handle_coverage = self.rect.h / self.element.rect.h

    @property
    def _child_elements(self) -> Iterable[Element]:
        return itertools.chain(super()._child_elements, (self._scrollbar,))

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == VALUEMODIFIED and event.element is self._scrollbar:
            with event.animation:
                self.scroll_value = self.scrollbar.value
            return True

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_value -= event.precise_y * 5

        return super()._event(event)

    @property
    def scroll_value(self) -> float:
        return self._scroll_value

    @scroll_value.setter
    def scroll_value(self, value: float) -> None:
        value = round(pygame.math.clamp(value, 0, self._max_scroll_value), 10)
        if value == self._scroll_value:
            return
        self._scroll_value = value
        position = PivotablePosition(-self._scroll_value, 0, watching=self)
        self.cascading.add(Element.x(position))
        self.cascading.add(Element.y(~position))
        self.scrollbar.value = value

    @scrollbar.setter
    def scrollbar(self, value: ScrollBar):
        self.removing_element(self._scrollbar)
        with self.adding_element(value) as element:
            self._scrollbar = element
        self._scrollbar_added(scrollbar=element)

    def make_visible(self, element: Element) -> None:
        if self in element.ancestry:
            with EaseOut(0.1):
                if element.rect.y + element.rect.h > self.rect.y + self.rect.h:
                    self.scroll_value += element.rect.y - self.rect.y - self.rect.h + element.rect.h
                if element.rect.y + element.rect.h < self.rect.y:
                    self.scroll_value += element.rect.y - self.rect.y
            return
        self.parent.make_visible(element)
