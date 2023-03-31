import pygame
from typing import Optional
from ember.material.material import Material
from ember.material.shape.shape import Shape

class Capsule(Shape):
    def __init__(self,
                 material: Optional[Material] = None,
                 color: Optional[pygame.Color] = None):

        super().__init__(material, color)

    def _create_surface(self, size):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        radius = size[1] / 2

        pygame.draw.circle(surface, (0, 0, 0), (radius, radius), radius)
        pygame.draw.circle(surface, (0, 0, 0), (size[0]-radius, radius), radius)

        pygame.draw.rect(surface, (0, 0, 0), (radius, 0, size[0] - radius * 2, size[1]))
        return surface

