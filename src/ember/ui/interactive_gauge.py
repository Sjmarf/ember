from typing import Optional, Union, Sequence
from abc import ABC
import pygame

from .gauge import Gauge
from ember.base.can_disable import CanDisable
from ember.base.has_primary_child import HasPrimaryChild
from ember.base.can_focus import CanFocus
from ember.base.click_activate_hybrid import ClickActivateHybrid

from .. import common as _c
from ember.axis import Axis, HORIZONTAL


class InteractiveGauge(Gauge, CanDisable, HasPrimaryChild, CanFocus, ClickActivateHybrid, ABC):
    scroll_to_adjust: bool = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _update(self) -> None:
        super()._update()
        if self.clicked and not self.disabled:
            progress = (_c.mouse_pos[self._axis] - self.rect[self._axis]) / self.rect[
                2 + self._axis
            ]
            if self._axis == HORIZONTAL:
                self.progress = progress
            else:
                self.progress = 1 - progress    
            
    def _event(self, event: pygame.event.Event) -> bool:
        if super()._event(event):
            return True
        
        if (
            event.type == pygame.MOUSEWHEEL
            and self.hovered
            and not self.disabled
            and self.scroll_to_adjust
        ):
            if self._axis == HORIZONTAL:
                if event.precise_x:
                    self.progress -= event.precise_x / 10
                else:
                    self.progress -= event.precise_y / 10
            else:
                self.progress -= event.precise_y / 10

        return False
