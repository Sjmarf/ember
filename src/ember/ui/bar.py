from abc import ABC, abstractmethod

from .gauge import Gauge
from ember import log
from ember.ui.single_element_container import SingleElementContainer
from ember.ui.panel import Panel

from ..material import Material

from ember.ui.element import Element
from .handled_element import UpdatingHandleElement

from ..event import VALUEMODIFIED

from ..size import FILL, PivotableSize
from ember.position import (
    LEFT,
    BOTTOM,
    PivotablePosition,
)

from ember.on_event import on_event
from ember.axis import Axis, HORIZONTAL


class Bar(UpdatingHandleElement, Gauge, SingleElementContainer, ABC):
    def __init__(self, *args, axis: Axis = HORIZONTAL, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, back_panel=Panel(None, y=0, size=FILL), axis=axis
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
