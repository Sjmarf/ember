from typing import Union, Optional, Sequence, TYPE_CHECKING
import pygame
from abc import ABC, abstractmethod

from .element import Element
from ember import log
from ember.trait import Trait
from ember.trait.cascading_trait_value import CascadingTraitValue
from ember.position import (
    Position,
    load_position,
    CENTER,
    PositionType,
    SequencePositionType,
    DualPosition,
)

from ember import log

from ember.animation.animation_context import AnimationContext
from ember.axis import HORIZONTAL
from ember.utility.geometry_vector import GeometryVector

if TYPE_CHECKING:
    from .view_layer import ViewLayer


class HasGeometry(Element, ABC):
    x: Trait[Position] = Trait(
        default_value=CENTER,
        on_update=lambda self: self._geometry_trait_modified("x"),
        default_cascade_depth=1,
        load_value_with=load_position,
    )

    y: Trait[Position] = Trait(
        default_value=CENTER,
        on_update=lambda self: self._geometry_trait_modified("y"),
        default_cascade_depth=1,
        load_value_with=load_position,
    )

    def __init__(
        self,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        layer: Optional["ViewLayer"] = None,
        can_focus: bool = False,
    ):
        self.rect = pygame.FRect(0, 0, 0, 0)
        """
        A :code:`pygame.FRect` object containing the absolute position and size of the element. Read-only.
        """

        self._int_rect = pygame.Rect(0, 0, 0, 0)

        self._can_focus: bool = can_focus

        if pos is not None:
            if isinstance(pos, Sequence):
                x, y = pos
            elif isinstance(pos, DualPosition):
                x, y = pos.x, pos.y
            else:
                x, y = pos, pos

        self.x = x
        self.y = y

        self.visible: bool = True
        """
        Is :code:`True` when any part of the element is visible on the screen. Read-only.
        """

        self._animation_contexts: list[AnimationContext] = []

        if CascadingTraitValue.context_depth > 0:
            CascadingTraitValue.new_elements.append(self)

        super().__init__(layer=layer)

        self._dimension_calculation_cache: dict[GeometryVector, GeometryVector] = {}

    def unpack(self) -> tuple["HasGeometry", ...]:
        return (self,)

    def build(self) -> None:
        if self._has_built:
            return
        self._has_built = True
        with log.size.indent("Building...", self):
            self._build()

    def update_rect(
        self,
        surface: pygame.Surface,
        x: Optional[float] = None,
        y: Optional[float] = None,
        w: Optional[float] = None,
        h: Optional[float] = None,
    ) -> None:
        if None in (x, y, w, h):
            raise ValueError(
                f"Missing value for updated element geometry - ({x}, {y}, {w}, {h})"
            )

        if self in self.layer.rect_update_queue:
            log.size.info(
                "Element is queued for update but recieved an update first, removing from list.",
                self,
            )
            self.layer.rect_update_queue = list(
                filter(lambda a: a is not self, self.layer.rect_update_queue)
            )

        if self.rect[:] == (x, y, w, h):
            log.size.info("Size didn't change, cutting chain...")
            return

        self.rect.update(x, y, w, h)
        self._int_rect.update(
            int(x),
            int(y),
            int(w),
            int(h),
        )

        with log.size.indent(
            f"Rect updating: [{self.rect.x:.2f}, {self.rect.y:.2f}, {self.rect.w:.2f}, {self.rect.h:.2f}].",
            self,
        ):
            self._update_rect(surface, x, y, w, h)

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        ...

    def update_rect_next_tick(self) -> None:
        """
        On the next view update, call update_rect for this element.
        """
        if (
            self.layer is not None
            and self.parent is not None
            and self.parent not in self.layer.rect_update_queue
        ):
            log.size.info(
                f"Queued parent {self.parent} for rect update next tick.", self
            )
            self.layer.rect_update_queue.append(self.parent)
        else:
            log.size.info("No layer - could not queue rect update.", self)

    def render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used internally by the library.
        """
        self._render(surface, offset, alpha=alpha)

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        """
        Used intenally by the library.
        """

    def update(self) -> None:
        """
        Used internally by the library. Updates the element, with transitions taken into consideration.
        """
        for anim_context in self._animation_contexts[:]:
            if anim_context._update():
                anim_context._finish()
                self._animation_contexts.remove(anim_context)
        self._update()

    def _update(self) -> None:
        """
        Used intenally by the library.
        """

    def event(self, event: pygame.event.Event) -> bool:
        return self._event(event)

    def _event(self, event: pygame.event.Event) -> bool:
        """
        Called by the parent of the element for each Pygame event,
        with the pygame event object passed to the method.
        """
        return False

    def get_x(
        self, container_width: float, element_width: Optional[float] = None
    ) -> float:
        return self.x.get(
            container_width, self.rect.w if element_width is None else element_width
        )

    def get_y(
        self, container_height: float, element_height: Optional[float] = None
    ) -> float:
        return self.y.get(
            container_height, self.rect.h if element_height is None else element_height
        )

    def get_dimensions(
        self,
        proposed_size: GeometryVector,
    ) -> GeometryVector:
        if (vector := self._dimension_calculation_cache.get(proposed_size)) is not None:
            log.size.info(f"Retrieved cached value for {proposed_size} - {vector}...", self)
            vector.axis = proposed_size.axis
            return vector

        with log.size.indent(f"Calculating dimensions for {proposed_size}", self):
            vector = self._get_dimensions(proposed_size)
            log.size.info(f"Calculated size - {vector}", self)
        vector.axis = proposed_size.axis
        self._dimension_calculation_cache[proposed_size] = vector
        return vector

    @abstractmethod
    def _get_dimensions(
        self,
        proposed_size: GeometryVector,
    ) -> GeometryVector:
        ...

    @property
    def rel_pos1(self) -> Position:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.x
        return self.y

    @property
    def rel_pos2(self) -> Position:
        if self._pivotable_parent.axis == HORIZONTAL:
            return self.y
        return self.x

    def is_animating(self, trait: Trait) -> bool:
        return any(i.trait_context.trait == trait for i in self._animation_contexts)
