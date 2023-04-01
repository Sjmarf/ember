import pygame
import logging
from typing import Union, Optional

from ember import common as c
from ember.utility.size_element import size_element
from ember.material.material import Material


class AverageColor(Material):
    def __init__(self,
                 hsv_adjustment: tuple[int,int,int] = (0,0,0)):
        super().__init__()
        self.hsv_adjustment = hsv_adjustment

    def render_surface(self, element, surface, pos, size, alpha):
        color = pygame.Color(pygame.transform.average_color(surface,(pos,size)))
        if self.hsv_adjustment:
            hsva = color.hsva

            color.hsva = (max(0,min(360,int(hsva[0]+self.hsv_adjustment[0]) % 360)),
                          max(0,int(min(hsva[1]+self.hsv_adjustment[1], 100))),
                          max(0,int(min(hsva[2]+self.hsv_adjustment[2], 100))), 100)

        if element not in self._cache or self._cache[element].get_size() != size or \
                self._cache[element].get_at((0,0)) != color:
            self._cache[element] = pygame.Surface(size,pygame.SRCALPHA)
            self._cache[element].fill(color)
            self._cache[element].set_alpha(alpha)
            return True

        self._cache[element].set_alpha(alpha)
        return False
