from abc import ABC
from tkinter import HORIZONTAL
from typing import Optional, Generic, TypeVar
from .element import Element

from ember.trait import Trait
from ember.axis import Axis, VERTICAL
from ember import log


def _axis_updated(self) -> None:
    self.update_ancestry(self.ancestry)
    with log.size.indent("Axis modified:"):
        self.update_min_size_next_tick(must_update_parent=True)


class CanPivot(Element, ABC):
    axis = Trait(default_value=VERTICAL, on_update=_axis_updated)

    def __init__(self, *args, axis: Axis | None = None, **kwargs) -> None:
        self._set_pivot_axis(axis)
        super().__init__(*args, **kwargs)
    
    def _set_pivot_axis(self, axis: Axis | None) -> None:
        """
        Exists so that it can be overriden by subclasses
        """
        self.axis = axis

    def get_x(
        self, container_width: float, element_width: Optional[float] = None
    ) -> float:
        return self.x.get(
            container_width,
            self.rect.w if element_width is None else element_width,
            self.axis,
        )

    def get_y(
        self, container_height: float, element_height: Optional[float] = None
    ) -> float:
        return self.y.get(
            container_height,
            self.rect.h if element_height is None else element_height,
            self.axis,
        )

    def get_w(self, max_width: float = 0) -> float:
        return self.w.get(self._min_size.w, max_width, self.rect.h, axis=self.axis)

    def get_h(self, max_height: float = 0) -> float:
        return self.h.get(self._min_size.h, max_height, self.rect.w, axis=self.axis)


Element._CanPivot = CanPivot

T = TypeVar("T")

class LockedAxis(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value
    
    def __get__(self, instance, owner) -> T:
        return self._value
        

class HorizontalLocked(CanPivot, ABC):
    axis = LockedAxis(HORIZONTAL)
    
    def _set_pivot_axis(self, axis: Axis | None) -> None:
        ...

class VerticalLocked(CanPivot, ABC):
    axis = LockedAxis(VERTICAL)

    def _set_pivot_axis(self, axis: Axis | None) -> None:
        ...