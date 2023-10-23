from abc import ABC
import pygame

from .gauge import Gauge
from ember.ui.can_disable import CanDisable
from ember.ui.has_primary_child import HasPrimaryChild
from ember.ui.can_focus import CanFocus
from ember.ui.click_activate_hybrid import ClickActivateHybrid

from .. import common as _c
from ember.axis import HORIZONTAL

from ember.event import CLICKEDDOWN
from ember.on_event import on_event


class InteractiveGauge(
    Gauge, CanDisable, HasPrimaryChild, CanFocus, ClickActivateHybrid, ABC
):
    scroll_to_adjust: bool = True
    steps: int = 10

    class ValueCause(Gauge.ValueCause):
        CLICK = Gauge.ValueCause.Cause()
        DRAG = Gauge.ValueCause.Cause()
        SCROLL = Gauge.ValueCause.Cause()
        KEY = Gauge.ValueCause.Cause()

    def _move_to_mouse_pos(self, cause: ValueCause.Cause) -> None:
        progress = (_c.mouse_pos[self._axis] - self.rect[self._axis]) / self.rect[
            2 + self._axis
        ]
        if self._axis == HORIZONTAL:
            progress = 1 - progress
        self._set_progress(1 - progress, cause)

    def _update(self) -> None:
        super()._update()
        if self.clicked and not self.disabled:
            self._move_to_mouse_pos(self.ValueCause.DRAG)

    @on_event(CLICKEDDOWN)
    def _click_to_adjust_value(self) -> None:
        self._move_to_mouse_pos(self.ValueCause.CLICK)

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
                    self._set_progress(
                        self.progress - event.precise_x / self.steps,
                        self.ValueCause.SCROLL,
                    )
                else:
                    self._set_progress(
                        self.progress - event.precise_y / self.steps,
                        self.ValueCause.SCROLL,
                    )
            else:
                self._set_progress(
                    self.progress - event.precise_y / self.steps,
                    self.ValueCause.SCROLL,
                )
            return True

        if event.type == pygame.KEYDOWN and self.activated:

            if event.key == (pygame.K_LEFT, pygame.K_DOWN)[self._axis]:
                self._set_progress(
                    self.progress - 1 / self.steps,
                    self.ValueCause.KEY,
                )
                return True
            elif event.key == (pygame.K_RIGHT, pygame.K_UP)[self._axis]:
                self._set_progress(
                    self.progress + 1 / self.steps,
                    self.ValueCause.KEY,
                )
                return True

        return False
