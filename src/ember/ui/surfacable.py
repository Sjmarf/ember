import abc
import pygame

from .has_geometry import HasGeometry

class Surfacable(HasGeometry):
    """
    Represents an Element that has a surface directly tied to it. :py:class:`ember.transition.SurfaceFade`
    only works with Surfacable elements.
    """

    @abc.abstractmethod
    def _get_surface(self, alpha: int = 255) -> pygame.Surface:
        pass

    @abc.abstractmethod
    def _draw_surface(
            self,
            surface: pygame.Surface,
            offset: tuple[int, int],
            my_surface: pygame.Surface,
    ) -> None:
        pass

    def _render(self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255) -> None:
        self._draw_surface(surface, offset, self._get_surface(alpha))
