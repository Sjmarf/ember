from abc import ABC, abstractmethod

from typing import Optional

import pygame
from .geometric_container import GeometricContainer
from .box import Box

from ember import common as c
from ember import log


class MaskedContainer(GeometricContainer, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._subsurface: pygame.Surface | None = None

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        super()._update_rect(
            self._get_subsurface(surface),
            x,
            y,
            w,
            h,
        )

    def render(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        super().render(self._get_subsurface(surface), (0, 0), alpha)

    def _get_subsurface(self, surface: pygame.Surface) -> pygame.Surface:
        if (
            self._subsurface is None
            or self._subsurface.get_parent() is not surface
            or (int(self.rect.w), int(self.rect.h)) != self._subsurface.get_size()
            or (int(self.rect.x), int(self.rect.y)) != self._subsurface.get_offset()
        ):
            self._subsurface = surface.subsurface(self.rect)
            log.size.info(f"Created subsurface with rect {self.rect}", self)
        return self._subsurface

    def event(self, event: pygame.event.Event) -> bool:
        if event.type in {
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        } and not self.rect.collidepoint(c.mouse_pos):
            event.is_masked = True
        return super().event(event)


class MaskedBox(MaskedContainer, Box):
    pass
