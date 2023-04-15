import pygame
import logging
from typing import Union, Optional

from .. import common as c
from ..utility.size_element import size_element
from .material import Material


class StretchedSurface(Material):
    def __init__(self, surface: Union[str, pygame.Surface],
                 edge: tuple[int, int, int, int] = (5, 5, 5, 5)):

        super().__init__()
        self.surface = pygame.image.load(surface).convert_alpha() if type(surface) is str else surface
        self.edge = edge

    def render_surface(self, element, surface: pygame.Surface, pos, size, alpha):
        if element in self._cache and self._cache[element].get_size() == size:
            surf = self._cache[element]
            surf.set_alpha(alpha)
            return False

        else:
            surf = size_element(self.surface, size, self.edge)
            self._cache[element] = surf
            surf.set_alpha(alpha)
            return True
