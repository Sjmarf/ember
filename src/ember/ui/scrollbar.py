from abc import ABC, abstractmethod

from .gauge import Gauge
from ember import log
from ember.ui.single_element_container import SingleElementContainer
from ember.ui.panel import Panel

from ..material import Material

from ember.ui.element import Element
from .handled_element import UpdatingHandleElement

from ..event import VALUEMODIFIED

from ..size import FILL, PivotableSize, RATIO
from ember.position import LEFT, BOTTOM, PivotablePosition, AnchorPosition

from ember.on_event import on_event
from ember.axis import Axis, HORIZONTAL

from .slider import Slider


class ScrollBar(Slider, ABC):
    def __init__(self, *args, handle_coverage: float = 0.5, **kwargs) -> None:

        self._handle_coverage: float = handle_coverage

        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return "<ScrollBar>"

    def _update_handle_sizes(self) -> None:
        size = PivotableSize(FILL * self._handle_coverage, FILL, watching=self)
        self.cascading.add(Element.w(size))
        self.cascading.add(Element.h(~size))

    @property
    def handle_coverage(self) -> float:
        return self._handle_coverage

    @handle_coverage.setter
    def handle_coverage(self, value: float) -> None:
        self._handle_coverage = value
        self._update_handle_sizes()
