import pygame
from .. import common as _c
from .base.slider import Slider

from .base.mixin.content_pos_direction import VerticalContentPos
from .base.mixin.content_size_direction import VerticalContentSize


class VSlider(VerticalContentPos, VerticalContentSize, Slider):
    def move_to_mouse(self) -> None:
        handle = self._elements[self.handle_element_index]
        padding = handle.h.get(handle._min_h, self.rect.h) / 2

        self.progress = pygame.math.clamp(
            (_c.mouse_pos[1] - self.rect.y - padding) / (self.rect.h - padding * 2),
            0,
            1,
        )

    def _update(self) -> None:
        if self.clicked_keyboard:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.shift_value(-_c.delta_time, self.MovementCause.KEY)
            elif keys[pygame.K_DOWN]:
                self.shift_value(_c.delta_time, self.MovementCause.KEY)

    def _event(self, event: pygame.event.Event) -> bool:
        if self.clicked_keyboard and event.type == pygame.KEYDOWN and event.key in {pygame.K_UP, pygame.K_DOWN}:
            return True
        if event.type == pygame.MOUSEWHEEL and self.hovered:
            if abs(event.precise_y) >= 0.1:
                self.shift_value(event.precise_y / 20, cause=self.MovementCause.SCROLL)
                return True
        return super()._event(event)
