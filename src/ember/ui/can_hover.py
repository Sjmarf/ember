import pygame

from typing import TYPE_CHECKING

from ember.ui.element import Element
from ember.event import HOVERED, UNHOVERED

from ember import common as _c

if TYPE_CHECKING:
    pass


class CanHover(Element):
    def __init__(self, *args, **kwargs) -> None:
        self._hovered: bool = False
        super().__init__(*args, **kwargs)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if getattr(event, "is_masked", False):
                hovered = False
            else:
                hovered = self.rect.collidepoint(_c.mouse_pos)
            if hovered != self._hovered:
                self._hovered = hovered
                if hovered:
                    self._post_event(HOVERED)
                else:
                    self._post_event(UNHOVERED)
        return super()._event(event)

    @property
    def hovered(self) -> bool:
        return self._hovered
