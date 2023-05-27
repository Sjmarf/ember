import pygame
import pygame.gfxdraw
from typing import Optional
from ..material import Material
from .shape import Shape

from ...common import ColorType

from .draw_circle import draw_ellipse


class Ellipse(Shape):
    def __init__(
        self,
        material: Optional[Material] = None,
        color: Optional[ColorType] = None,
        outline: int = 0,
        antialias: bool = True,
    ):
        super().__init__(material, color, antialias, outline)

    def __repr__(self) -> str:
        return "<Ellipse>"

    def _create_surface(self, size: tuple[float, float]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        draw_ellipse(surface, (0, 0, *size), self._antialias, self._outline)
        return surface
