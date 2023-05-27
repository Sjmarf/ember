import pygame
from typing import Optional
from ..material import Material
from .shape import Shape

from ...common import ColorType

from .draw_circle import draw_circle


class RoundedRect(Shape):
    def __init__(
        self,
        material: Optional[Material] = None,
        color: Optional[ColorType] = None,
        radius: int = 20,
        outline: int = 0,
        antialias: bool = True,
    ):
        super().__init__(material, color, antialias, outline)

        self._radius = radius
        self._corner_surf: Optional[pygame.Surface] = None
        self.set_radius(radius)

    def __repr__(self) -> str:
        if self._color:
            return "<RoundedRect({}, {}, {})>".format(*self._color)
        elif self._material:
            return f"<RoundedRect({self._material})>"
        else:
            return f"<RoundedRect>"

    def _update_generic_surface(self) -> None:
        self._corner_surf = pygame.Surface(
            (self._radius, self._radius), pygame.SRCALPHA
        )
        draw_circle(
            self._corner_surf, (0, 0), self._radius, self.antialias, self._outline
        )
        self._clear_cache()

    def _create_surface(self, size: tuple[float, float]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)

        surface.blit(
            self._corner_surf, (size[0] - self._radius, size[1] - self._radius)
        )
        surface.blit(
            pygame.transform.rotate(self._corner_surf, 90), (size[0] - self._radius, 0)
        )
        surface.blit(pygame.transform.rotate(self._corner_surf, 180), (0, 0))
        surface.blit(
            pygame.transform.rotate(self._corner_surf, 270), (0, size[1] - self._radius)
        )

        if self._outline:
            offset = self._outline / 2 - 0.5
            pygame.draw.line(  # Top
                surface,
                (0, 0, 0),
                (self._radius, offset),
                (size[0] - self._radius, offset),
                self._outline,
            )
            pygame.draw.line(  # Bottom
                surface,
                (0, 0, 0),
                (self._radius, size[1] - offset),
                (size[0] - self._radius, size[1] - offset),
                self._outline,
            )
            pygame.draw.line(  # Left
                surface,
                (0, 0, 0),
                (offset, self._radius),
                (offset, size[1] - self._radius),
                self._outline,
            )
            pygame.draw.line(  # Right
                surface,
                (0, 0, 0),
                (size[0] - offset, self._radius),
                (size[0] - offset, size[1] - self._radius),
                self._outline,
            )
        else:
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (self._radius, 0, size[0] - self._radius * 2, size[1]),
            )
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (0, self._radius, size[0], size[1] - self._radius * 2),
            )
        return surface

    def _set_radius(self, radius: int) -> None:
        self.set_radius(radius)

    def set_radius(self, radius: int) -> None:
        self._radius = radius
        self._update_generic_surface()

    radius: int = property(
        fget=lambda self: self._radius,
        fset=_set_radius,
        doc="The corner radius, in pixels, of the rounded rectangle.",
    )
