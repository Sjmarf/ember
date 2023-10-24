import pygame
import pygame.gfxdraw
import math
from typing import Optional
from ..material import Material
from .base_shape import Shape

from ...common import ColorType

from.draw_circle import draw_arc

DEG_90 = math.radians(90)
DEG_180 = math.radians(180)

class Capsule(Shape):
    """
    Masks the given material or color to a capsule (tic-tac) shape.
    """
    def __init__(self,
                 material: Optional[Material] = None,
                 color: Optional[ColorType] = None,
                 outline: int = 0,
                 antialias: bool = True
                 ):

        super().__init__(material, color, antialias, outline)
        
        self.antialias: bool = antialias
        """
        When :code:`True`, the rounded edges will be anti-aliased.
        """ 
        
        self.outline: int = outline
        """
        The thickness of the shape outline. If set to 0, the ellipse will be filled with no outline.
        """
    
    def __repr__(self) -> str:
        return "<Capsule>"

    def _create_surface(self, size: tuple[float, float]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        offset = self._outline / 2 - 0.5

        if size[0] >= size[1]:
            radius = size[1] // 2
            draw_arc(surface, (radius, radius), radius, self.antialias, self.outline, DEG_90, -DEG_90)
            draw_arc(surface, (size[0]-radius, radius), radius, self.antialias, self.outline, -DEG_90, DEG_90)
            if self._outline:
                pygame.draw.line(
                    surface,
                    (0, 0, 0),
                    (radius, offset),
                    (size[0] - radius, offset),
                    self._outline,
                )
                pygame.draw.line(
                    surface,
                    (0, 0, 0),
                    (radius, size[1] - offset),
                    (size[0] - radius, size[1] - offset),
                    self._outline,
                )
            else:
                pygame.draw.rect(surface, (0, 0, 0), (radius, 0, size[0] - radius * 2, size[1]), self.outline)
            
        else:
            radius = size[0] // 2
            draw_arc(surface, (radius, radius), radius, self.antialias ,self.outline, 0, DEG_180)
            draw_arc(surface, (radius, size[1]-radius), radius, self.antialias, self.outline, DEG_180, 0)
            if self._outline:
                pygame.draw.line(
                    surface,
                    (0, 0, 0),
                    (offset, radius),
                    (offset, size[1] - radius),
                    self._outline,
                )
                pygame.draw.line(
                    surface,
                    (0, 0, 0),
                    (size[0] - offset, radius),
                    (size[0] - offset, size[1] - radius),
                    self._outline,
                )
            else:
                pygame.draw.rect(surface, (0, 0, 0), (0, radius, size[0], size[1] - radius * 2), self.outline)
            
        return surface

