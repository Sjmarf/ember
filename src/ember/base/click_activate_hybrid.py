from typing import TYPE_CHECKING, Union

import pygame

from ember.base.element import Element
from ember.base.can_hover import CanHover
from ember.event import CLICKEDDOWN, CLICKEDUP, ACTIVATED, DEACTIVATED, UNFOCUSED

from ember import common as _c

if TYPE_CHECKING:
    pass

from ..on_event import on_event

class ClickActivateHybrid(CanHover, Element):
    
    def __init__(self, *args, **kwargs) -> None:
        self.clicked: bool = False
        self.activated: bool = False
        super().__init__(*args, **kwargs)
        
    @on_event(UNFOCUSED)
    def _deactivate(self) -> None:
        self.activated = False
        self._post_event(DEACTIVATED)
        
    def _event(self, event: pygame.event.Event) -> bool:
        if super()._event(event):
            return True
        
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            self.clicked = self.hovered
            if self.clicked:
                self._post_event(CLICKEDDOWN)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked:
                self.clicked = False
                self._post_event(CLICKEDUP)
                return True

        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_RETURN
            and self.layer.element_focused is self
        ):
            self.activated = not self.activated
            self._post_event(ACTIVATED)
            return True
            
        return False