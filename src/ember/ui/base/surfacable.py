import abc
import pygame

from .element import Element

class Surfacable(Element, abc.ABC):
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
