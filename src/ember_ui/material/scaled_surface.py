import pygame
from typing import Union, Sequence, Optional, Any, TYPE_CHECKING

from .material import MaterialWithSizeCache

if TYPE_CHECKING:
    from ember_ui.ui.base.element import Element


class ScaledSurface(MaterialWithSizeCache):
    """
    Stretches a pygame Surface while preserving the edges of the Surface.
    """

    def __init__(
        self,
        surface: Union[str, pygame.Surface],
        smooth: bool = True,
        alpha: int = 255,
    ):
        super().__init__(alpha)
        self._surface: pygame.Surface = (
            pygame.image.load(surface).convert_alpha()
            if isinstance(surface, str)
            else surface
        )

        self.smooth: bool = smooth
        """
        If True, pygame.transform.smoothscale is used. If False, pygame.transform.scale is used.
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
        func = pygame.transform.smoothscale if self.smooth else pygame.transform.scale
        return func(self._surface, size)

    @property
    def surface(self) -> pygame.Surface:
        """
        The surface to scale.
        """
        return self._surface

    @surface.setter
    def surface(self, value: pygame.Surface) -> None:
        self._surface = value
        self.clear_cache()
