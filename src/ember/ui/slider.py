from abc import ABC, abstractmethod

from .gauge import Gauge
from ember import log
from ember.ui.single_element_container import SingleElementContainer
from ember.ui.panel import Panel

from ..material import Material

from ember.ui.has_geometry import HasGeometry
from .handled_element import UpdatingHandleElement
from .can_pivot import CanPivot
from .geometric_container import GeometricContainer

from ..event import VALUEMODIFIED

from ..size import FILL, PivotableSize, RATIO
from ember.position import LEFT, BOTTOM, PivotablePosition, AnchorPosition

from ember.on_event import on_event
from ember.axis import Axis, HORIZONTAL


class Slider(UpdatingHandleElement, Gauge, CanPivot, SingleElementContainer, GeometricContainer, ABC):
    def __init__(self, *args, axis: Axis | None = None, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, back_panel=Panel(None, y=0, size=FILL), axis=axis
        )

        self._update_handle_position()
        self._update_handle_size()

    def __repr__(self) -> str:
        return "<Slider>"

    def _update_handle_size(self) -> None:
        size = PivotableSize(RATIO, FILL, watching=self)
        self.cascading.add(HasGeometry.w(size))
        self.cascading.add(HasGeometry.h(~size))

    @on_event(VALUEMODIFIED)
    def _update_handle_position(self):
        with log.size.indent("Updating bar cascading sizes..."):
            self.cascading.add(
                HasGeometry.x(
                    PivotablePosition(
                        AnchorPosition(percent=self.progress), 0, watching=self
                    )
                )
            )
            self.cascading.add(
                HasGeometry.y(
                    PivotablePosition(
                        0, AnchorPosition(percent=1 - self.progress), watching=self
                    )
                )
            )

Slider.axis.default_value = HORIZONTAL
