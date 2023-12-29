from abc import ABC, abstractmethod

from .gauge import Gauge
from ember import log

from ember.ui.has_geometry import HasGeometry

from ..size import FILL, PivotableSize, RATIO
from ember.position import LEFT, BOTTOM, PivotablePosition, AnchorPosition
from .slider import Slider


class ScrollBar(Slider, ABC):
    invert_y_axis = False

    def __init__(self, *args, handle_coverage: float = 0.5, **kwargs) -> None:
        self._handle_coverage: float = handle_coverage

        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return "<ScrollBar>"

    def _update_handle_size(self) -> None:
        size = PivotableSize(FILL * self._handle_coverage, FILL, watching=self)
        self.cascading.add(HasGeometry.w(size))
        self.cascading.add(HasGeometry.h(~size))

    @property
    def handle_coverage(self) -> float:
        return self._handle_coverage

    @handle_coverage.setter
    def handle_coverage(self, value: float) -> None:
        self._handle_coverage = value
        self._update_handle_size()

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
                        0, AnchorPosition(percent=self.progress), watching=self
                    )
                )
            )
