import pygame
from typing import Optional
from ..material import Material
from .shape import Shape

class RoundedRect(Shape):
    def __init__(self,
                 material: Optional[Material] = None,
                 color: Optional[pygame.Color] = None,
                 radius: int = 20):

        super().__init__(material, color)
        self._radius = radius

        self.corner_surf: Optional[pygame.Surface] = None
        self.set_radius(radius)

    def __repr__(self):
        if self._color:
            return "<RoundedRect({}, {}, {})>".format(*self._color)
        elif self._material:
            return f"<RoundedRect({self._material})>"
        else:
            return f"<RoundedRect>"

    def set_radius(self, radius: int = 20):
        self._radius = radius
        self.corner_surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        pygame.draw.circle(self.corner_surf, (0, 0, 0), (0, 0), radius)
        self._cache.clear()

    def _create_surface(self, size):
        surface = pygame.Surface(size, pygame.SRCALPHA)

        surface.blit(self.corner_surf, (size[0] - self._radius, size[1] - self._radius))
        surface.blit(pygame.transform.rotate(self.corner_surf, 90), (size[0] - self._radius, 0))
        surface.blit(pygame.transform.rotate(self.corner_surf, 180), (0, 0))
        surface.blit(pygame.transform.rotate(self.corner_surf, 270), (0, size[1] - self._radius))

        pygame.draw.rect(surface, (0, 0, 0), (self._radius, 0, size[0] - self._radius * 2, size[1]))
        pygame.draw.rect(surface, (0, 0, 0), (0, self._radius, size[0], size[1] - self._radius * 2))
        return surface

    def _get_radius(self):
        return self._radius

    radius = property(
        fget=_get_radius,
        fset=set_radius
    )
