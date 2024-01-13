import pygame
import itertools
from abc import ABC
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    TypeVar,
    Iterable,
)
from ember.utility.geometry_vector import GeometryVector
from ember.utility.geometry_rect import GeometryRect
from ember.axis import Axis

from .container import Container
from .has_geometry import HasGeometry
from .has_variable_size import HasVariableSize

if TYPE_CHECKING:
    pass


T = TypeVar("T")


@dataclass
class LayoutBlueprint:
    size: GeometryVector
    placements: list["LayoutPlacement"]


@dataclass
class LayoutPlacement:
    element: HasGeometry
    rect: GeometryRect


class GeometricContainer(Container, HasVariableSize, ABC):
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
        blueprint = self.get_layout_blueprint(
            elements=tuple(self._elements_to_render),
            proposed_size=GeometryVector(w=w, h=h),
        )

        for placement in blueprint.placements:
            placement.rect.origin.w += x
            placement.rect.origin.h += y
            placement.element.update_rect(surface, *placement.rect)

    def _event(self, event: pygame.event.Event) -> bool:
        for i in reversed(tuple(self._elements_to_render)):
            if i is not None and i.event(event):
                return True
        return super()._event(event)

    def get_min_size(self, proposed_size: GeometryVector) -> GeometryVector:
        min_size = GeometryVector(20, 20)
        if self.w.min_value_intent:
            min_size.w = self.get_layout_blueprint(
                elements=tuple(self._elements_to_render),
                proposed_size=GeometryVector(w=0, h=proposed_size.h),
            ).size.w
        if self.h.min_value_intent:
            min_size.h = self.get_layout_blueprint(
                elements=tuple(self._elements_to_render),
                proposed_size=GeometryVector(w=proposed_size.w, h=0),
            ).size.h

        return min_size

    def get_layout_blueprint(
        self,
        elements: tuple[HasGeometry, ...],
        proposed_size: GeometryVector,
    ) -> LayoutBlueprint:
        placements: list[LayoutPlacement] = []

        total_size = GeometryVector(0,0)
        for element in elements:
            element_size = element.get_dimensions(proposed_size)
            total_size.w = max(total_size.w, element_size.w)
            total_size.h = max(total_size.h, element_size.h)
            placement = LayoutPlacement(
                element, GeometryRect(GeometryVector.ZERO, element_size)
            )
            placements.append(placement)

        if proposed_size.w != 0:
            total_size.w = proposed_size.w
        if proposed_size.h != 0:
            total_size.h = proposed_size.h

        for placement in placements:
            x = placement.element.get_x(total_size.w, placement.rect.size.w)
            y = placement.element.get_y(total_size.h, placement.rect.size.h)
            placement.rect.origin = GeometryVector(x, y)

        return LayoutBlueprint(size=total_size, placements=placements)

    @property
    def _elements_to_render(self) -> Iterable[HasGeometry]:
        return itertools.chain.from_iterable(
            element.unpack() for element in self._child_elements if element is not None
        )
