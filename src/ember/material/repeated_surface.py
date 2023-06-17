import pygame
import math
from typing import Union, Sequence, Optional, Any, TYPE_CHECKING

from .material import MaterialWithSizeCache
from ..position import PositionType, SequencePositionType, CENTER, Position

if TYPE_CHECKING:
    from ember.ui.base.element import Element


class RepeatedSurface(MaterialWithSizeCache):
    """
    Repeats a Pygame Surface to fill the material area
    """

    def __init__(
        self,
        surface: Union[str, pygame.Surface],
        content_x: Optional[PositionType] = CENTER,
        content_y: Optional[PositionType] = CENTER,
        alpha: int = 255,
    ):
        super().__init__(alpha)
        self._surface: pygame.Surface = (
            pygame.image.load(surface).convert_alpha()
            if isinstance(surface, str)
            else surface
        )

        self._content_x: Position = Position._load(content_x)
        self._content_y: Position = Position._load(content_y)

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
        new_surface = pygame.Surface(size, pygame.SRCALPHA)
        new_surface.fill((30, 30, 30))
        surf_size = self._surface.get_size()

        offset_x = self._content_x.get(element, size[0], 0) % surf_size[0] - surf_size[0]
        offset_y = self._content_y.get(element, size[1], 0) % surf_size[1] - surf_size[1]

        print(size, (offset_x, offset_y), surf_size)

        for y in range(math.ceil(size[1] / surf_size[1]) + 1):
            for x in range(math.ceil(size[0] / surf_size[0]) + 1):
                new_surface.blit(
                    self._surface,
                    (offset_x + x * surf_size[0], offset_y + y * surf_size[1]),
                )
        return new_surface

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

    @property
    def content_x(self) -> Position:
        return self._content_x

    @content_x.setter
    def content_x(self, value: PositionType):
        self._content_x = Position._load(value)
        self.clear_cache()

    @property
    def content_y(self) -> Position:
        return self._content_y

    @content_y.setter
    def content_y(self, value: PositionType):
        self._content_y = Position._load(value)
        self.clear_cache()
