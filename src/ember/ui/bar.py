from abc import ABC, abstractmethod

from .gauge import Gauge
from ember import log
from ember.ui.multi_element_container import MultiElementContainer

from ..material import Material

from ember.ui.element import Element
from .two_panel_container import TwoPanelContainer

from ..event import VALUEMODIFIED

from ..size import FILL, PivotableSize
from ember.position import (
    LEFT,
    BOTTOM,
    PivotablePosition,
)

from ember.on_event import on_event
from ember.axis import Axis, HORIZONTAL


class Bar(TwoPanelContainer, Gauge, MultiElementContainer, ABC):

    def __init__(self, *args, axis: Axis = HORIZONTAL, **kwargs) -> None:
        super().__init__(*args,**kwargs, axis=axis)
        
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

        self.cascading.add(Element.x(PivotablePosition(LEFT, 0, watching=self)))
        self.cascading.add(Element.y(PivotablePosition(0, BOTTOM, watching=self)))

        size = PivotableSize(FILL * self._progress, FILL, watching=self)
        self.cascading.add(Element.w(size))
        self.cascading.add(Element.h(~size))

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

    @on_event(VALUEMODIFIED)
    def _update_panel_sizes(self):
        with log.size.indent("Updating bar cascading sizes..."):
            size = PivotableSize(FILL * self._progress, FILL, watching=self)
            self.cascading.add(Element.w(size))
            self.cascading.add(Element.h(~size))
            
            