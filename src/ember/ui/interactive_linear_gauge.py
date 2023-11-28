from abc import ABC
import pygame

from .gauge import Gauge
from ember.ui.can_disable import CanDisable
from ember.ui.can_focus import CanFocus
from ember.ui.can_pivot import CanPivot
from ember.ui.click_activate_hybrid import ClickActivateHybrid

from .. import common as _c
from ember.axis import HORIZONTAL, VERTICAL

from ember.event import CLICKEDDOWN
from ember.on_event import on_event


class InteractiveLinearGauge(Gauge, CanDisable, CanFocus, ClickActivateHybrid, CanPivot, ABC):
    scroll_to_adjust: bool = True
    center_handle_on_pickup: bool = True
    keyboard_adjustment_steps: int = 10
    scroll_speed: float = 0.1
    invert_y_axis: bool = True

    class ValueCause(Gauge.ValueCause):
        CLICK = Gauge.ValueCause.Cause()
        DRAG = Gauge.ValueCause.Cause()
        SCROLL = Gauge.ValueCause.Cause()
        KEY = Gauge.ValueCause.Cause()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handle_pickup_point: float = 0

    def _move_to_mouse_pos(
        self,
        cause: ValueCause.Cause,
        handle_rect: pygame.FRect = pygame.FRect(0, 0, 0, 0),
    ) -> None:
        x = self.rect[self.axis] + handle_rect[2 + self.axis] / 2
        w = self.rect[2 + self.axis] - handle_rect[2 + self.axis]
        if w == 0:
            return
        rel_x = _c.mouse_pos[self.axis] - x

        if cause is InteractiveLinearGauge.ValueCause.CLICK:
            self._handle_pickup_point = 0
        if (not self.center_handle_on_pickup) and (
            handle_rect[self.axis]
            < _c.mouse_pos[self.axis]
            < handle_rect[self.axis] + handle_rect[2 + self.axis]
        ):
            if cause is InteractiveLinearGauge.ValueCause.CLICK:
                self._handle_pickup_point = (
                    _c.mouse_pos[self.axis] - handle_rect[self.axis] - handle_rect[2 + self.axis] / 2
                )
        rel_x -= self._handle_pickup_point

        progress = rel_x / w

        if self.axis == HORIZONTAL or not self.invert_y_axis:
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
            if self.axis == HORIZONTAL:
                if event.precise_x:
                    self._set_progress(
                        self.progress - event.precise_x * self.scroll_speed,
                        self.ValueCause.SCROLL,
                    )
                else:
                    self._set_progress(
                        self.progress - event.precise_y * self.scroll_speed,
                        self.ValueCause.SCROLL,
                    )
            else:
                self._set_progress(
                    self.progress - event.precise_y * self.scroll_speed,
                    self.ValueCause.SCROLL,
                )
            return True

        if event.type == pygame.KEYDOWN and self.activated:
            if event.key == (pygame.K_LEFT, pygame.K_DOWN)[self.axis]:
                progress = - 1 / (self.keyboard_adjustment_steps - 1)
                if self.axis == VERTICAL and self.invert_y_axis:
                    progress *= -1
                self._set_progress(
                    self.progress - progress,
                    self.ValueCause.KEY,
                )
                return True
            elif event.key == (pygame.K_RIGHT, pygame.K_UP)[self.axis]:
                progress = 1 / (self.keyboard_adjustment_steps - 1)
                if self.axis == VERTICAL and self.invert_y_axis:
                    progress *= -1
                self._set_progress(
                    self.progress - progress,
                    self.ValueCause.KEY,
                )
                return True

        return False
