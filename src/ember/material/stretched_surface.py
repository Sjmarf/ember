import pygame
from functools import partial
from typing import Union, Sequence, Optional, Any, TYPE_CHECKING
from os import PathLike, fspath

from ..utility.stretch_surface import stretch_surface
from .material import MaterialWithSizeCache

if TYPE_CHECKING:
    from ember.ui.base.element import Element


from ember._init import init_task

class StretchedSurface(MaterialWithSizeCache):
    """
    Stretches a pygame Surface while preserving the edges of the Surface.
    """

    def __init__(
        self,
        surface: Union[str, pygame.Surface, PathLike],
        edge: Union[int, Sequence[int]] = 5,
        alpha: int = 255,
    ):
        super().__init__(alpha)
        self.surface: Optional[pygame.Surface] = None
        init_task(partial(self.load_surface, surface))

        """
        The surface to stretch.
        """
        self._edge: Sequence[int] = (edge, edge, edge, edge) if isinstance(edge, int) else edge
        """
        (left, right, top, bottom). The number of pixels from each side that should be kept intact.
        """

    def load_surface(self, surface: Union[str, pygame.Surface, PathLike]) -> None:
        if isinstance(surface, pygame.Surface):
            self.surface = surface
        else:
            if isinstance(surface, PathLike):
                surface = fspath(surface)
            self.surface = pygame.image.load(surface).convert_alpha()

    def __repr__(self) -> str:
        return "<StretchedSurface>"

    def _needs_to_render(
        self,
        element: "Element",
        surface: pygame.Surface,
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> bool:
        return element not in self._cache or self._cache[element].get_size() != size

    def _render_surface(
        self,
        element: Optional["Element"],
        surface: Optional[pygame.Surface],
        pos: tuple[float, float],
        size: tuple[float, float],
    ) -> Any:
        return stretch_surface(self.surface, size, self.edge)

    @property
    def edge(self) -> Sequence[int]:
        return self._edge

    @edge.setter
    def edge(self, value: Sequence[int]):
        self._edge = value
        self.clear_cache()
