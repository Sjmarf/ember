import pygame
from typing import Union, Sequence, Optional, Any, TYPE_CHECKING

from ..utility.stretch_surface import stretch_surface
from .material import MaterialWithSizeCache

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class StretchedSurface(MaterialWithSizeCache):
    """
    Stretches a pygame Surface while preserving the edges of the Surface.
    """

    def __init__(
        self,
        surface: Union[str, pygame.Surface],
        edge: Sequence[int] = (5, 5, 5, 5),
        alpha: int = 255,
    ):
        super().__init__(alpha)
        self.surface: pygame.Surface = (
            pygame.image.load(surface).convert_alpha()
            if isinstance(surface, str)
            else surface
        )
        """
        The surface to stretch.
        """
        self.edge: Sequence[int] = edge
        """
        (left, right, top, bottom). The number of pixels from each side that should be kept intact.
        """

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
