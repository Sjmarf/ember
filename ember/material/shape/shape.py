import pygame
from typing import Optional
from ember.material.material import Material


class Shape(Material):
    def __init__(self,
                 material: Optional[Material] = None,
                 color: Optional[pygame.Color] = None):

        super().__init__()
        if color is not None and material is not None:
            raise ValueError("You must provide either a color or material, not both.")
        self._material = material
        self._color = color

    def _create_surface(self, size) -> pygame.Surface:
        pass

    def render_surface(self, element, surface: pygame.Surface, pos, size, alpha):
        if self._material:
            if self._material.render_surface(element, surface, pos, size, 255) or element not in self._cache:
                surface = self._create_surface(size)
                surface.blit(self._material.get_surface(element), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
                surface.set_alpha(alpha)
                self._cache[element] = surface

        elif self._color:
            if element not in self._cache or self._cache.get(element).get_size() != size:
                surface = self._create_surface(size)
                surface.fill(self._color, special_flags=pygame.BLEND_RGB_ADD)
                surface.set_alpha(alpha)
                self._cache[element] = surface
