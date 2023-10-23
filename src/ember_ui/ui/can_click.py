from typing import TYPE_CHECKING

import pygame

from ember_ui.ui.element import Element
from ember_ui.ui.can_hover import CanHover
from ember_ui.event import CLICKEDDOWN, CLICKEDUP

if TYPE_CHECKING:
    pass

class CanClick(CanHover, Element):
    """
    This class is a mixin, and should not be instantiated directly.
    It provides functionality for clicking an element.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._clicked: bool = False
        super().__init__(*args, **kwargs)

    def _event(self, event: pygame.event.Event) -> bool:
        if super()._event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._clicked = self.hovered
            if self._clicked:
                self._post_event(CLICKEDDOWN)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._clicked:
                self._clicked = False
                self._post_event(CLICKEDUP)
                return True

        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
            and self.layer.element_focused is self
        ):
            self._clicked = True
            self._post_event(CLICKEDDOWN)
            return True

        elif event.type == pygame.KEYUP and event.key == pygame.K_RETURN:
            if self._clicked:
                self._clicked = False
                self._post_event(CLICKEDUP)
                return True

        elif (
            event.type == pygame.JOYBUTTONDOWN
            and event.button == 0
            and self.layer.element_focused is self
        ):
            self._clicked = True
            self._post_event(CLICKEDDOWN)
            return True

        elif event.type == pygame.JOYBUTTONUP and event.button == 0:
            if self._clicked:
                self._clicked = False
                self._post_event(CLICKEDUP)
                return True

        return False

    @property
    def clicked(self) -> bool:
        return self._clicked
