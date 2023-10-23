import pygame
from typing import Optional, Union
from .. import common as _c
from .base.slider import Slider


from .base.mixin.content_pos_direction import HorizontalContentPos
from .base.mixin.content_size_direction import HorizontalContentSize


class HSlider(HorizontalContentPos, HorizontalContentSize, Slider):
    def move_to_mouse(self) -> None:
        handle = self._elements[self.handle_element_index]
        padding = handle.w.get(handle._min_w, self.rect.w) / 2

        self.progress = pygame.math.clamp(
            (_c.mouse_pos[0] - self.rect.x - padding) / (self.rect.w - padding * 2),
            0,
            1,
        )

    def _update(self) -> None:
        if self.clicked_keyboard:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.shift_value(-_c.delta_time, self.MovementCause.KEY)
            elif keys[pygame.K_RIGHT]:
                self.shift_value(_c.delta_time, self.MovementCause.KEY)

    def _event(self, event: pygame.event.Event) -> bool:
        if self.clicked_keyboard and event.type == pygame.KEYDOWN and event.key in {
            pygame.K_LEFT,
            pygame.K_RIGHT,
        }:
            return True
        if event.type == pygame.MOUSEWHEEL and self.hovered:
            if abs(event.precise_x) >= 0.1:
                self.shift_value(-event.precise_x / 20, cause=self.MovementCause.SCROLL)
                return True
        return super()._event(event)
