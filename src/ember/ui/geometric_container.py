import pygame
import itertools
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import (
    Optional,
    TYPE_CHECKING,
    Generator,
    Type,
    Sequence,
    Union,
    TypeVar,
    Iterable,
)

from ember.ui.element import Element
from ember.ui.context_manager import ContextManager

from ember import log
from ember.common import ElementType
from ember.trait.trait import Trait
from ember.trait.cascade_repository import CascadeRepository
from ember.trait.cascading_trait_value import CascadingTraitValue
from ember.trait import trait_layer
from ember.trait.trait_layer import TraitLayer
from ember.ui.text import Text
from ember.size import Fill

from .container import Container
from .has_geometry import HasGeometry

if TYPE_CHECKING:
    pass


T = TypeVar("T")


class GeometricContainer(Container, HasGeometry, ABC):
    """
    Base class for Containers that have geometry.
    """
    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        for i in self._elements_to_render: 
            if i is not None:
                i.render(surface, offset, alpha=alpha)

    def _update(self) -> None:
        super()._update()
        for i in self._elements_to_render: 
            if i is not None:
                i.update()

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        for element in self._elements_to_render: 
            if element is None:
                continue

            element_w = element.get_w(w)
            element_h = element.get_h(h)
            element_x = x + element.get_x(w, element_w)
            element_y = y + element.get_y(h, element_h)

            element.visible = self.visible
            element.update_rect(surface, element_x, element_y, element_w, element_h)

    def _update_min_size(self) -> None:
        self._min_size.w = 0
        for element in self._elements_to_render: 
            if element is None or isinstance(element.w, Fill):
                continue
            if (w := element.get_w()) > self._min_size.w:
                self._min_size.w = w

        self._min_size.h = 0
        for element in self._elements_to_render: 
            if element is None or isinstance(element.h, Fill):
                continue
            if (h := element.get_h()) > self._min_size.h:
                self._min_size.h = h

    def _event(self, event: pygame.event.Event) -> bool:
        
        for i in reversed(tuple(self._elements_to_render)):
            if i is not None and i.event(event):
                return True
        return super()._event(event)

    @property
    def _elements_to_render(self) -> Iterable[HasGeometry]:
        return itertools.chain.from_iterable(element.unpack() for element in self._child_elements if element is not None)
   