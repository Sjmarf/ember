import pygame
from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import Enum

from ember import common as _c
from ember import log

from .multi_element_container import MultiElementContainer

if TYPE_CHECKING:
    from .element import Element


class Scroll(MultiElementContainer, ABC):
    class MovementCause(Enum):
        SCROLL = 0
        VISIBILITY = 1
        SET = 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._subsurf: Optional[pygame.Surface] = None
        self.scrollable_element_index: int = -1

        self._scroll: float = 0

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        if (
            self._subsurf is None
            or (*self._subsurf.get_abs_offset(), *self._subsurf.get_size())
            != self._int_rect
            or self._subsurf.get_abs_parent() is not surface.get_abs_parent()
        ) and self.visible:
            parent_surface = surface.get_abs_parent()
            rect = self._int_rect.copy().clip(parent_surface.get_rect())
            self._subsurf = parent_surface.subsurface(rect)

        super()._update_rect(self._subsurf, x, y, w, h)
        self.scroll = self._scroll

    def _render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        super()._render(self._subsurf, offset, alpha)

    @property
    def scroll(self) -> float:
        return self._scroll

    @scroll.setter
    def scroll(self, value: float) -> None:
        self.set_scroll(value)

    @property
    def scrollable_element(self) -> Optional["Element"]:
        return self._elements[self.scrollable_element_index]

    def set_scroll(
        self, value: float, cause: MovementCause = MovementCause.SET
    ) -> None:
        if self.scrollable_element.rect.h < self.rect.h:
            val = 0
        else:
            val = pygame.math.clamp(
                value,
                0,
                self.scrollable_element.rect.h - self.rect.h,
            )
        if self._scroll != val:
            self._scroll = val
            event = pygame.event.Event(
                SCROLLMOVED, element=self, value=self._scroll, cause=cause
            )
            self._post_event(event)

    def _event(self, event: pygame.event.Event) -> bool:
        if super()._event(event):
            return True
        if event.type == pygame.MOUSEWHEEL and self.hovered:
            if abs(event.precise_y) >= 0.1:
                self.set_scroll(
                    self._scroll - event.precise_y * 5, cause=self.MovementCause.SCROLL
                )
                return True
        return False

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if (
            direction
            in {
                _c.FocusDirection.SELECT,
                _c.FocusDirection.IN,
                _c.FocusDirection.IN_FIRST,
            }
            and self._elements
        ):
            log.nav.info(f"-> child {self._elements[self.scrollable_element_index]}.")
            return self._elements[self.scrollable_element_index]._focus_chain(
                _c.FocusDirection.IN_FIRST
            )
        else:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)
