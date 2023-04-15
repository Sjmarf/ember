import pygame
import logging
from typing import Union, Optional, Tuple

from .. import common as c
from ..utility.size_element import size_element
from ..material.material import Material


class Color(Material):
    def __init__(self, color: Union[pygame.Color, tuple[int, int, int], str], outline=0, alpha=255):
        super().__init__()
        self.color = color
        self.outline = outline
        self.alpha = alpha

    def render_surface(self, element, surface, pos, size, alpha):
        if element not in self._cache or self._cache[element].get_size() != size or \
                self._cache[element].get_at((0,0)) != self.color:
            self._cache[element] = pygame.Surface(size,pygame.SRCALPHA)
            pygame.draw.rect(self._cache[element], self.color, (0,0, *size), self.outline)
            self._cache[element].set_alpha(alpha * self.alpha / 255)
            return True

        self._cache[element].set_alpha(alpha*self.alpha/255)
        return False
